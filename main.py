import configparser
import pandas as pd
from sklearn.preprocessing import OneHotEncoder


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

    encoder = OneHotEncoder()
    columnes = ['state_0', 'state_1', 'state_2','state_3','state_4','state_5','state_6','state_7','state_8']
    data_file[columnes] = pd.DataFrame(encoder.fit_transform(data_file[['STATE']]).toarray())
    data_file.to_csv(filter_file, index=False, sep=',')


def city_feature_encoding():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', low_memory=False)

    encoder = TargetEncoder()
    encoder.fit(X=data_file['CITY'], y=data_file['PHONEAREACODE'])
    data_file['CITY_ENCODING'] = encoder.transform(data_file['CITY'])
    data_file.to_csv(filter_file, index=False, sep=',')


if __name__ == '__main__':
    filter_columns_file()
    state_feature_encoding()
    city_feature_encoding()

