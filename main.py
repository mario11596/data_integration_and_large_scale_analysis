import configparser
import pandas as pd

import category_encoders as ce
config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
filter_file = config['filepath_raw']
def filter_columns_file():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)

    # delete records with only numbers in name
    check_contain_numeric_name = data_file["NAME"].str.isnumeric()
    index = check_contain_numeric_name.index[check_contain_numeric_name == True].tolist()
    data_file.drop(labels=index, axis=0, inplace=True)

    # remove symbols from name
    data_file["NAME"].replace('\W', '', regex=True, inplace=True)
    data_file["NAME"].replace('', None, regex=True, inplace=True)

    # delete records that have null name
    data_file.dropna(subset=['NAME'], inplace=True)
    data_file.to_csv(filter_file, index=False, sep=',')

def state_feature_encoding():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)

    encoder = ce.BaseNEncoder(cols=['STATE'], return_df=True, base=8)
    data_file[['STATE_ENCODED_0', 'STATE_ENCODED_1']] = encoder.fit_transform(data_file['STATE'].copy())
    data_file.to_csv(filter_file, index=False, sep=',')



def city_feature_encoding():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)

    encoder = ce.TargetEncoder(cols=['CITY'])
    data_file['CITY_ENCODED'] = encoder.fit_transform(data_file['CITY'], data_file['PHONEAREACODE'])
    print(data_file['CITY_ENCODED'])
    data_file.to_csv(filter_file, index=False, sep=',')

if __name__ == '__main__':
    filter_columns_file()
    state_feature_encoding()
    city_feature_encoding()

