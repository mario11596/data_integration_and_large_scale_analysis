from __future__ import annotations
from dataclasses import dataclass
import re
import pandas as pd
import phonenumbers as phn
from phonenumbers import geocoder
from phonenumbers import PhoneNumber
from sklearn.preprocessing import OneHotEncoder

#TODO no address also dropped?, 
#     first phone area good enought?

#TODO check
#decide if New York == NY/Queens/Brooklyn/etc.? or stay with NY/Queens/Brooklyn
#   e.g 243 W 38th Street, New York, NY, NY
#       943 Coney Island Avenue, Brooklyn, NY, NY

states = {
    'Alaska' : 'AK',
    'Alabama' : 'AL', 
    'Arkansas' : 'AR', 
    'Arizona' : 'AZ', 
    'California' : 'CA', 
    'Colorado' : 'CO', 
    'Connecticut' : 'CT', 
    'District of Columbia' : 'DC',
    'Delaware' : 'DE', 
    'Florida' : 'FL', 
    'Georgia' : 'GA', 
    'Guam' : 'GU', 
    'Hawaii' : 'HI', 
    'Iowa' : 'IA', 
    'Idaho' : 'ID', 
    'Illinois' : 'IL', 
    'Indiana' : 'IN', 
    'Kansas' : 'KS', 
    'Kentucky' : 'KY', 
    'Louisiana' : 'LA', 
    'Marshall Islands' : 'MH', 
    'Massachusetts' : 'MA', 
    'Maryland' : 'MD', 
    'Maine' : 'ME', 
    'Michigan' : 'MI', 
    'Minnesota' : 'MN', 
    'Missouri' : 'MO', 
    'Mississippi' : 'MS', 
    'Montana' : 'MT', 
    'North Carolina' : 'NC',
    'North Dakota' : 'ND',
    'Northern Mariana Island' : 'MP', 
    'Nebraska' : 'NE',
    'New Hampshire' : 'NH',
    'New Jersey' : 'NJ',
    'New Mexico' : 'NM',
    'Nevada' : 'NV', 
    'New York' : 'NY',
    'Ohio' : 'OH', 
    'Oklahoma' : 'OK', 
    'Oregon' : 'OR', 
    'Pennsylvania' : 'PA', 
    'Puerto Rico' : 'PR', 
    'Rhode Island' : 'RI',
    'South Carolina' : 'SC',
    'South Dakota' : 'SD',
    'Tennessee' : 'TN', 
    'Texas' : 'TX', 
    'Utah' : 'UT', 
    'Virginia' : 'VA', 
    'Virgin Islands' : 'VI', 
    'Vermont' : 'VT', 
    'Washington' : 'WA', 
    'Washington State' : 'DC', 
    'Wisconsin': 'WI', 
    'West Virginia': 'WV',
    'Wyoming': 'WY', 
}

new_york_options = {
    "Queens" : "New York",
    "NY" : "New York",
    "NYC" : "New York",
    "Brooklyn" : "New York",
}

@dataclass
class LocationInfo:
    phone_area: list
    city: str
    state: str
    phonenumber: PhoneNumber

def parse_segments(address_segments: list(str)) -> tuple(str, str):
    city = None
    state = None
    for segment in reversed(address_segments):
        if segment is None or segment == "":
            continue
        if state is None:
            #if any(char.isdigit() for char in segment):
            pattern = re.compile("[A-Z][A-Z]")
            found_match = re.search(pattern, segment)
            if found_match:
                state = found_match.group(0)
                continue
                #print(state)
                
        if city is None and any(char.isdigit() for char in segment) is False:
            pattern = re.compile("[A-Z][A-Z]")
            found_match = re.search(pattern, segment)
            if found_match:
                continue
            city = segment
            #print(city)
        
        #if city in new_york_options:
        #    city = "New York"
    
    return city, state
        
def complete_info(locationInfo: LocationInfo, region_map: dict) -> bool:
    if (locationInfo.phone_area is None) and ((locationInfo.city is not None) and (locationInfo.state is not None)):
        #TODO check if good enough
        if locationInfo.city in region_map:
            for location in region_map[locationInfo.city]:
                if location.state == locationInfo.state:
                    locationInfo.phone_area = location.phone_area
                    return True
        return False
    
    if (locationInfo.city is None) and ((locationInfo.phone_area is not None) and (locationInfo.state is not None)):
        area_string = geocoder.description_for_number(locationInfo.phonenumber, "en")
        if area_string is not None and area_string != "":
            if len(area_string.split(", ")) == 1:
                locationInfo.city = area_string
            else:
                locationInfo.city = area_string.split(", ")[0]
            return True
        return False
    
    if (locationInfo.state is None) and ((locationInfo.city is not None) and (locationInfo.phone_area is not None)):
        area_string = geocoder.description_for_number(locationInfo.phonenumber, "en")
        if area_string is not None and area_string != "":
            if len(area_string.split(", ")) == 1:
                locationInfo.state = states[area_string]
            else:
                locationInfo.state = area_string.split(", ")[1]
            return True
        return False
    
    if (locationInfo.state is not None) and (locationInfo.city is not None) and (locationInfo.phone_area is not None):
        return True

    return False

def add_to_map(location: LocationInfo, region_map: dict):
    if location.city not in region_map:
        region_map[location.city] = [location]
    else:
        region_map[location.city].append(location)
    return

def write_table(df_table: pd.DataFrame, region_map: dict, location_list: list(LocationInfo), output_name: str):
    df_table = df_table.drop("RATING", axis=1)
    df_table = df_table.drop("NO_OF_REVIEWS", axis=1)
    
    df_table["CITY"] = [entry.city for entry in location_list]
    df_table["STATE"] = [entry.state for entry in location_list]
    df_table["PHONEAREACODE"] = [''.join(entry.phone_area) for entry in location_list]
    
    with open("data/" + output_name + ".csv", "w") as output_file:
        df_table.to_csv(output_file, ",", index=False)
    return

def write_debug(region_map: dict, output_name: str):
    cities_list = pd.DataFrame(list(region_map.items()))

    with open("data/" + output_name + ".csv", "w") as output_file:
        cities_list.to_csv(output_file, ",", index=False)
        pass
    return

def clean_address(csv_file, output_name: str):
    df_table = pd.read_csv(csv_file)
    
    region_map = {}
    location_list = []
    
    total_records = 0
    rejected_records = 0
    #debug_count = 0
    for phone, address in zip(df_table["PHONENUMBER"], df_table["ADDRESS"]):
        new_location = LocationInfo(None, None, None, None)
        #debug_count += 1
        total_records += 1
        
        parsed_number = phn.parse(phone, "US")
        if phn.is_possible_number(parsed_number) and phn.is_valid_number(parsed_number):
            new_location.phonenumber = parsed_number
            phone_string = phn.national_significant_number(parsed_number)
            ndc_length = phn.length_of_national_destination_code(parsed_number)
            new_location.phone_area = [phone_string[0:ndc_length], 
                                       phone_string[ndc_length:ndc_length + 3]]
        
        address_segments = address.split(", ")
        if len(address_segments) >= 2:
            new_location.city, new_location.state = parse_segments(address_segments)
        
        #print(new_location)
        if complete_info(new_location, region_map) is True:
            add_to_map(new_location, region_map)
            location_list.append(new_location)
        else:
            rejected_records += 1
            idx = df_table[((df_table.ADDRESS == address) & (df_table.PHONENUMBER == phone))].index
            df_table = df_table.drop(idx, axis=0)
        #print(new_location)
        
        #if debug_count >= 100:
        #    break
    
    percentage = (rejected_records / total_records) * 100
    print(f'{rejected_records}/{total_records} ({percentage:.2f}%) rejected.')
    write_table(df_table, region_map, location_list, output_name)
    write_debug(region_map, "city_names")
    return

def filter_columns_file(outputname):
    data_file = pd.read_csv(filepath_or_buffer=outputname, delimiter=',', low_memory=False)

    # delete records with only numbers in name
    check_contain_numeric_name = data_file["NAME"].str.isnumeric()
    index = check_contain_numeric_name.index[check_contain_numeric_name == True].tolist()
    data_file.drop(labels=index, axis=0, inplace=True)

    # remove symbols from name
    data_file["NAME"].replace('\W', '', regex=True, inplace=True)
    data_file["NAME"].replace('', None, regex=True, inplace=True)

    # delete records that have null name
    data_file.dropna(subset=['NAME'], inplace=True)
    data_file.to_csv(outputname, index=False, sep=',')

def state_feature_encoding(outputname):
    data_file = pd.read_csv(filepath_or_buffer=outputname, delimiter=',', low_memory=False)

    encoder = OneHotEncoder()
    columnes = ['state_0', 'state_1', 'state_2','state_3','state_4','state_5','state_6','state_7','state_8']
    data_file[columnes] = pd.DataFrame(encoder.fit_transform(data_file[['STATE']]).toarray())
    data_file.to_csv(outputname, index=False, sep=',')


def city_feature_encoding(outputname):
    data_file = pd.read_csv(filepath_or_buffer=outputname, delimiter=',', low_memory=False)

    encoder = TargetEncoder()
    encoder.fit(X=data_file['CITY'], y=data_file['PHONEAREACODE'])
    data_file['CITY_ENCODING'] = encoder.transform(data_file['CITY'])
    data_file.to_csv(outputname, index=False, sep=',')

def cleaning_feature_encoding(outputname : str):
    filter_columns_file(outputname)
    state_feature_encoding(outputname)
    city_feature_encoding(outputname)

    return

def main():
    with open("data/yelp.csv", "+r") as yelp_csv:
        clean_address(yelp_csv, "yelp_loc_cleaned")
        cleaning_feature_encoding("yelp_loc_cleaned.csv")
        
    #with open("data/zomato.csv", "+r") as zomato_csv:
    #    clean_address(zomato_csv, "zomato_loc_cleaned")
    #    cleaning_feature_encoding("data/zomato_loc_cleaned.csv")
        
    return


if __name__ == "__main__":
    main()