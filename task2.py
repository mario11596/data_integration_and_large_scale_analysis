from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import os
import re
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
input_file = os.path.join(config["filepath_data"], config['filename_comp'])
pred_file = os.path.join(config["filepath_data"], config['filename_pred'])
out_file = os.path.join(config["filepath_data"], config['filename_out3'])

class AddressState(Enum):
    NUMBER = 0
    NAME = 1
    CITY = 2
    STATE = 3

@dataclass
class AddressInfo:
    streetnumber: int = None
    street: str = None
    extra: str = None
    city: str = None
    state: str = None
    
    @property
    def as_list(self):
        return [self.streetnumber, self.street, self.city, self.state, self.extra]

replace = {"street": " St",
           "avenue": " Ave",
           "boulevard": " Blvd",
           "road": " Rd",
           "#": " Ste",
           "lane": " Ln"}

ignore = {'ste', 'suite'}

#TODO how to handle numbers in streetnames (e.g 9th St, Suite 112, etc.)
#TODO two entries are edgecases and cant be handled properly (187,188 in sep_address), maybe consider removing those two entries?

def parse_address(address: str) -> AddressInfo:
    info = AddressInfo()
    current_state = 0
    for segment in address.split(','):
        for word in segment.split(' '):
            if word == '':
                continue
            #print(word)
            match AddressState(current_state):
                case AddressState.NUMBER:
                    if info.streetnumber is None and any(char.isdigit() for char in word):
                        info.streetnumber = int(re.search(r'\d+', word).group(0))
                        current_state = AddressState.NAME.value
                    elif info.extra is None:
                        #info.streetnumber = -1
                        info.extra = word
                    else:
                        #info.streetnumber = -1
                        info.extra += ' '
                        info.extra += word
                case AddressState.NAME:
                    if info.street is None:
                        info.street = word
                    elif word.lower() in replace:
                        info.street += replace[word.lower()]
                    else:
                        info.street += ' '
                        info.street += word
                case AddressState.CITY:
                    if word.lower() in ignore:
                        continue
                    if info.city is None and all(char.isalpha() for char in word):
                        info.city = word
                    elif all(char.isalpha() for char in word):
                        info.city += ' '
                        info.city += word
                case AddressState.STATE:
                    if info.state is None and not any(char.isdigit() for char in word):
                        pattern = re.compile("[A-Z][A-Z]")
                        found_match = re.search(pattern, segment)
                        if found_match:
                            info.state = found_match.group(0)
        if info.street is not None and info.state is None:
            if current_state > 2:
                break
            current_state += 1
    return info

def get_index(idx: pd.Index) -> dict:
    print(idx.values)
    if idx.values[0] == "#key=_id":
        return {'lname': 3, 'rname': 6, 'laddress': 5, 'raddress': 8}
    elif idx.values[0] == "ltable.name":
        return {'lname': 0, 'rname': 2, 'laddress': 1, 'raddress': 3}

def separate_address(input_csv: os.PathLike) -> pd.DataFrame:
    inputdf = pd.read_csv(input_csv, delimiter=',', low_memory=False)
    #print(inputdf)
    
    index = get_index(inputdf.columns)
    print(index)
    
    newdf = dict()
    idx = 0
    for _, row in inputdf.iterrows():
        print(row)
        infol = parse_address(str(row.iloc[index['laddress']])) 
        infor = parse_address(str(row.iloc[index['raddress']]))
        new_entry = [row.iloc[index['lname']]]
        new_entry.extend(infol.as_list)
        new_entry.append(row.iloc[index['rname']])
        new_entry.extend(infor.as_list)
        newdf[idx] = new_entry
        idx += 1
    #for row in inputdf.iterrows():
    #go through address
    # city, state, street, streetnumber + remaining id
    #print(newdf)
    header = ['lname', 'lStreetNumber', 'lStreetAddress', 'lCity', 'lState', 'lExtraInfo',
              'rname', 'rStreetNumber', 'rStreetAddress', 'rCity', 'rState', 'rExtraInfo']
    df = pd.DataFrame.from_dict(newdf, orient='index', columns=header)
    df = df.dropna(how='all', subset=['lname', 'rname', 'lStreetNumber', 'rStreetNumber'])
    drop_idx = df[df['lname'] == 'ltable.NAME'].index
    df = df.drop(drop_idx, axis=0)
    return df

def main():
    separated_addresses1 = separate_address(input_file)
    separated_addresses2 = separate_address(pred_file)
    #concat and export to csv file only for debugging purposes.
    frames = [separated_addresses1, separated_addresses2]
    concat_file = pd.concat(frames)
    print(concat_file)
    concat_file.to_csv(out_file, ",")
    return

if __name__ == "__main__":
    main()