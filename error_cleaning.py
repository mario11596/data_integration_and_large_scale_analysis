import os
import re
from dataclasses import dataclass
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
error_file = os.path.join(config["filepath_data"], config['filename_err'])
clean_file = os.path.join(config["filepath_data"], config['filename_cle'])
test_file = os.path.join(config["filepath_data"], config['filename_orig2'])

@dataclass
class ErrorInfo:
    data: pd.DataFrame = None
    corrupt_amount: int = 0
    fixed_amount: int = 0
    made_changes: bool = False
    typo: int = 0
    missing: int = 0
    outlier: int = 0
    
    def __add__(self, o):
        if not isinstance(o, ErrorInfo):
            raise NotImplementedError
        return ErrorInfo(o.data, self.corrupt_amount + o.corrupt_amount, 
                                 self.fixed_amount + o.fixed_amount,
                                 self.made_changes | o.made_changes,
                                 self.typo + o.typo,
                                 self.missing + o.missing,
                                 self.outlier + o.outlier)
    
    @property
    def get_report(self):
        s  = f"Number of corrupt Instances: {self.corrupt_amount}\n"
        s += f"Number of fixed Instances {self.fixed_amount}\n"
        s += f"Tuples with Typos (Symbols rather than correct character): {self.typo}\n"
        s += f"Tuples with missing Values: {self.missing}\n"
        s += f"Tuples outliers: {self.outlier}"
        return s

char_mapping_dict = {"@": "a",
                     "!": "i",
                     "&": "n",
                     "3": "e",
                     "9": "g",
                     "$": "s"}

def separate_name(string: str) -> tuple:
    seg_list = []
    use_regex = []
    for segment in string.split(" "):
        seg_list.append(segment)
        if len(string) >= 1:
            if all(char.isdigit() for char in segment):
                use_regex.append(False)
            elif all(char.isalnum() for char in segment) and segment[0].isdigit():
                use_regex.append(False)
            else:
                use_regex.append(True)
    return seg_list, use_regex

def replace_regex(string_list: list, use_regex: list, repl_list: dict) -> str:
    new_list = []
    for new_string, apply_re in zip(string_list, use_regex):
        if apply_re:
            for char, replace in zip(repl_list, repl_list.values()):
                pattern = rf'((\s*)([^{re.escape(char)}\s]+)({re.escape(char)})|({re.escape(char)})([^{re.escape(char)}\s]+)(\s*))'
                new_string = re.sub(pattern, rf'\2\3{replace}\6\7', new_string)
        new_list.append(new_string)
    return ' '.join(new_list)

def replace_wrong_chars(index: int, row: pd.Series, data: pd.DataFrame) -> ErrorInfo:
    new_data = data.copy(deep=True)
    corrupted = 0
    replaced = 0
    changes = False
    name = str(row.loc['NAME'])
    address = str(row.loc['ADDRESS'])
    fixed_name = replace_regex(*separate_name(name), char_mapping_dict)
    fixed_street = replace_regex(*separate_name(address), char_mapping_dict)
    if id(name) != id(fixed_name):
        new_data.loc[index, 'NAME'] = fixed_name
        corrupted = 1
        replaced += 1
        changes = True
    if id(address) != id(fixed_street):
        new_data.loc[index, 'ADDRESS'] = fixed_street
        corrupted = 1
        replaced += 1
        changes = True
    return ErrorInfo(data=new_data, typo=replaced, made_changes=changes, corrupt_amount=corrupted)

def remove_missing_phonenumber(index: int, row: pd.Series, data: pd.DataFrame) -> ErrorInfo:
    new_data = data.copy(deep=True)
    phone_number = str(row.loc['PHONENUMBER'])
    if '(' not in phone_number:
        new_data.loc[index, 'PHONENUMBER'] = "Unknown"
        return ErrorInfo(data=new_data, missing=1, fixed_amount=1, made_changes=True, corrupt_amount=1)
    return ErrorInfo(data=new_data, missing=0, made_changes=False, corrupt_amount=0)

def test_accuracy(df1: pd.DataFrame):
    correct_instance = 0
    incorrect_instance = 0
    test_df = pd.read_csv(test_file, delimiter=',')
    for tuple_fixed, tuple_test in zip(df1.iterrows(), test_df.iterrows()):
        conditions = [tuple_fixed[1].loc['NAME'] == tuple_test[1].loc['NAME'], 
                      tuple_fixed[1].loc['ADDRESS'] == tuple_test[1].loc['ADDRESS'],
                      tuple_fixed[1].loc['PHONENUMBER'] == "Unknown" and not '(' in tuple_test[1].loc['PHONENUMBER'] or tuple_fixed[1].loc['PHONENUMBER'] != "Unknown"]
        if all(comparison is True for comparison in conditions):
            correct_instance += 1
        else:
            incorrect_instance += 1

    accuracy = correct_instance / (correct_instance + incorrect_instance) * 100
    print(f"Accuracy when compared to original yelp.csv is: {accuracy:.2f}%")

def clean_data() -> ErrorInfo:
    df = pd.read_csv(error_file, delimiter=',')
    info = ErrorInfo(df)
    for index, row in df.iterrows():
        info += replace_wrong_chars(index, row, info.data)
        info += remove_missing_phonenumber(index, row, info.data)
        if info.made_changes:
            info.made_changes = False
        info.fixed_amount += 1
    return info

def main():
    clean_info = clean_data()
    clean_info.data.to_csv(clean_file, ',', index=False)
    test_accuracy(clean_info.data)
    print(clean_info.get_report)

if __name__ == "__main__":
    main()