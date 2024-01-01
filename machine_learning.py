from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import os
import re
import numpy as np
import pandas as pd
import configparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.svm import SVC

config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
input_file = os.path.join(config["filepath_data"], config['filename_comp'])
pred_file = os.path.join(config["filepath_data"], config['filename_pred'])
out_file = os.path.join(config["filepath_data"], config['filename_out3'])
gold_file = os.path.join(config["filepath_data"], config['filename_gold'])


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


def parse_address(address: str) -> AddressInfo:
    info = AddressInfo()
    current_state = 0
    for segment in address.split(','):
        for word in segment.split(' '):
            if word == '':
                continue
            match AddressState(current_state):
                case AddressState.NUMBER:
                    if info.streetnumber is None and any(char.isdigit() for char in word):
                        info.streetnumber = int(re.search(r'\d+', word).group(0))
                        current_state = AddressState.NAME.value
                    elif info.extra is None:
                        info.extra = word
                    else:
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
    if idx.values[0] == "#key=_id":
        return {'lname': 3, 'rname': 6, 'laddress': 5, 'raddress': 8}
    elif idx.values[0] == "ltable.name":
        return {'lname': 0, 'rname': 2, 'laddress': 1, 'raddress': 3}


def separate_address(input_csv: os.PathLike) -> pd.DataFrame:
    inputdf = pd.read_csv(input_csv, delimiter=',', low_memory=False)

    index = get_index(inputdf.columns)

    newdf = dict()
    idx = 0
    for _, row in inputdf.iterrows():
        infol = parse_address(str(row.iloc[index['laddress']]))
        infor = parse_address(str(row.iloc[index['raddress']]))
        new_entry = [row.iloc[index['lname']]]
        new_entry.extend(infol.as_list)
        new_entry.append(row.iloc[index['rname']])
        new_entry.extend(infor.as_list)
        newdf[idx] = new_entry
        idx += 1

    header = ['lname', 'lStreetNumber', 'lStreetAddress', 'lCity', 'lState', 'lExtraInfo',
              'rname', 'rStreetNumber', 'rStreetAddress', 'rCity', 'rState', 'rExtraInfo']
    df = pd.DataFrame.from_dict(newdf, orient='index', columns=header)
    df = df.dropna(how='all', subset=['lname', 'rname', 'lStreetNumber', 'rStreetNumber'])
    drop_idx = df[df['lname'] == 'ltable.NAME'].index
    df = df.drop(drop_idx, axis=0)
    return df

def feature_encodig(dataset):
    dataset['lStreetAddress'] = dataset['lStreetAddress'].fillna('')

    vector = TfidfVectorizer()

    for each_column in dataset.columns:
        if each_column in ['lname', 'rname', 'lStreetAddress', 'rStreetAddress']:
            transformFit = vector.fit_transform(dataset[each_column])
            dataset[each_column] = np.mean(transformFit.toarray(), axis=1)

    return dataset


def machine_learning(dataset_train, dataset_predict):
    df = pd.read_csv(filepath_or_buffer=input_file, delimiter=',', skiprows=5)
    target = df['gold']

    test_gold = pd.read_csv(filepath_or_buffer=gold_file)
    test_gold = test_gold['gold']

    # edge case, problem with street number in these two records
    dataset_train = dataset_train.drop(labels=[190, 191], axis=0)
    target = target.drop(labels=[190, 191], axis=0)

    model = SVC()

    print("Grid search is running!")

    # hyperparameter Tuning with GridSearchCV
    param_options = {
        'C': [0.01, 0.1, 0.5, 1, 10, 100, 300, 500, 1000],
        'gamma': [1, 0.5, 0.1, 0.01, 0.001, 0.005, 0.0001],
        'kernel': ['rbf', 'sigmoid'],
    }

    grid_search = GridSearchCV(model, param_options, cv=3, scoring='accuracy', return_train_score=True)
    grid_search.fit(dataset_train, target)

    print("Grid search is done!")

    all_cv_results = grid_search.cv_results_

    for params, mean_score in zip(all_cv_results['params'], all_cv_results['mean_test_score']):
        print(f"Parameters: {params}, Mean Score: {mean_score}")

    print("Best Parameters: ", grid_search.best_params_)

    # train model with best parameters found by GridSearchCV
    model = SVC(C= grid_search.best_params_['C'], gamma=grid_search.best_params_['gamma'], kernel=grid_search.best_params_['kernel'])

    three_fold_cv = KFold(n_splits=3, shuffle=True, random_state=42)

    cv_ml_scores = []
    i = 1
    for train_index, test_index in three_fold_cv.split(dataset_train, target):
        X_train, X_test = dataset_train.iloc[train_index, :], dataset_train.iloc[test_index, :]
        y_train, y_test = target.iloc[train_index], target.iloc[test_index]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        cv_ml_scores.append(accuracy)

        print(f"Accuracy for fold {i}: {accuracy:.4f}")
        i += 1

    print("\nCross-Validation Scores:", cv_ml_scores)

    prediction = model.predict(dataset_predict)

    accuracy = accuracy_score(test_gold, prediction)
    print("\nTest Score:", accuracy)

    return


def data_correction(dataset):
    dataset = dataset.drop(['lCity', 'rCity', 'lState', 'rState', 'lExtraInfo', 'rExtraInfo'], axis=1)
    return dataset


def main():
    separated_addresses1 = separate_address(input_file)
    separated_addresses2 = separate_address(pred_file)

    #concat and export to csv file only for debugging purposes
    #frames = [separated_addresses1, separated_addresses2]
    #concat_file = pd.concat(frames)
    #concat_file.to_csv(out_file, ",")

    separated_addresses1 = data_correction(separated_addresses1)
    separated_addresses1 = feature_encodig(separated_addresses1)
    separated_addresses2 = data_correction(separated_addresses2)
    separated_addresses2 = feature_encodig(separated_addresses2)

    machine_learning(separated_addresses1, separated_addresses2)

    return

if __name__ == "__main__":
    main()