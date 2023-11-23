import configparser
import pandas as pd
from category_encoders import *


config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
filter_file = config['filepath_raw']
def filter_columns_file():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)
    specific_column = data_file["NAME"]

    # string only has numbers
    check_contain_numeric_name = specific_column.str.isnumeric()
    index = check_contain_numeric_name.index[check_contain_numeric_name == True].tolist()
    data_file.drop(labels=index, axis=0, inplace=True)

    #string has strange letters
    data_file["NAME"].replace('\W', '', regex=True, inplace=True)
    data_file.to_csv(filter_file, index=False, sep=',')

    #strring has null
    data_file.dropna(subset=['NAME'], inplace=True)
    data_file.to_csv(filter_file, index=False, sep=',')

def state_feature_encoding():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)
    state_counts = data_file['STATE'].value_counts().to_dict()
    data_file['STATE_ENCODED'] = data_file['STATE'].map(state_counts)
    data_file.to_csv(filter_file, index=False, sep=',')


def city_feature_encoding():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)

    encoder = TargetEncoder()
    encoder.fit(X=data_file['CITY'], y=data_file['PHONEAREACODE'])

    values = encoder.transform(data_file['CITY_ENCODED'])
    data = pd.concat([data_file, values], axis=1)


if __name__ == '__main__':
    filter_columns_file()
    state_feature_encoding()
    city_feature_encoding()

