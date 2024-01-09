import os
from dataclasses import dataclass
import pandas as pd

@dataclass
class Classification:
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0
    new_matches: int = 0
    same_matches: int = 0

    def __add__(self, o):
        if not isinstance(o, Classification):
            raise NotImplementedError
        res = Classification(self.tp + o.tp, self.tn + o.tn, self.fp + o.fp, self.fn + o.fn, self.new_matches + o.new_matches, self.same_matches + o.same_matches)
        return res


def compare_row(row1: tuple, row2: tuple, gold: int) -> Classification:
    comp = Classification()

    if row1[0] == row2[0] and row1[1] == row2[1]:
        if row1[2] == row2[2]:
            comp.tp = row1[2]

            comp.tn = 1 - row1[2]

            if gold == 1:
                comp.same_matches += 1
        else:
            comp.fn = row2[2]
            comp.fp = 1 - row2[2]
    return comp


def penalize_remaining(df) -> Classification:
    cla = Classification()
    if df.empty:
        return cla
    for _, row in df.iterrows():
        cla.fn += row['gold']

    return cla


def scoring(csv_file: os.PathLike, matching_restaurant: dict) -> float:
    data_file = pd.read_csv(filepath_or_buffer=csv_file, delimiter=',', skiprows=range(0, 5))
    new_matches = []

    cla = Classification()

    df_gold = data_file[data_file['gold'] == 1]
    print(f"Labeled_data file length: {len(data_file['gold'])}, our file length: {len(matching_restaurant['gold'])}")
    print(f"Labeled_data gold: {len(df_gold)}, our matches 'gold': {len([x for x in matching_restaurant['gold'] if x == 1])}")

    previous_ltable = -1
    for ltable, rtable, gold in zip(matching_restaurant['ltable'], matching_restaurant['rtable'], matching_restaurant['gold']):

        if previous_ltable == -1:
            previous_ltable = ltable
            df_new = data_file[data_file['ltable._id'] == ltable]
        elif previous_ltable != ltable:
            cla += penalize_remaining(df_new)
            df_new = data_file[data_file['ltable._id'] == ltable]
            previous_ltable = ltable

        if not df_new.empty:
            found_entry = df_new[df_new['rtable._id'] == rtable]
            index = df_new[df_new['rtable._id'] == rtable].index
            if not found_entry.empty:
                row1 = (ltable, rtable, gold)
                row2 = (found_entry['ltable._id'].item(), found_entry['rtable._id'].item(), found_entry['gold'].item())
                cla += compare_row(row1, row2, gold)
                df_new = df_new.drop(index, axis=0)

        elif (rtable not in data_file['rtable._id'].values) and gold == 1:
            cla.tp += 1
            cla.new_matches += 1
            new_matches.append(("Yelp: " + str(rtable + 1), "Zomato: " + str(ltable)))

        elif (rtable not in data_file['rtable._id'].values) and gold == 0:
            cla.tn += 1

    acc = ((cla.tp + cla.tn) / (cla.tp + cla.tn + cla.fp + cla.fn)) * 100

    print(f"Accuracy of pipeline is {acc}")

    print(f"TP is {cla.tp}")
    print(f"TN is {cla.tn}")
    print(f"FP is {cla.fp}")
    print(f"FN is {cla.fn}")

    print(f"The number of matches records which are also in labeld_data.csv file: {cla.same_matches}")
    print(f"The number of matches records which are NOT in labeld_data.csv file: {cla.new_matches}")
    print(f"The additional IDs of matches records:")
    for record_tuple in new_matches:
        print("\n", record_tuple)