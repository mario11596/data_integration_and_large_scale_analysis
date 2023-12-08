import configparser
from dataclasses import dataclass
import pandas as pd

config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
filter_file = config['filepath_raw']

@dataclass
class Classification:
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0
    #same: int = 0
    
    def __add__(self, o):
        if not isinstance(o, Classification):
            raise NotImplementedError
        res = Classification(self.tp + o.tp, self.tn + o.tn, self.fp + o.fp, self.fn + o.fn)
        return res
        

def compare_row(row1: tuple, row2: tuple) -> Classification:
    comp = Classification()
    #print(f"ids: {row1[0]}, {row1[1]} and {row2[0]}, {row2[1]}")
    if row1[0] == row2[0] and row1[1] == row2[1]:
        if row1[2] == row2[2]:
            comp.tp = row1[2]
            #comp.same = row1[2]
            comp.tn = 1 - row1[2]
        else:
            comp.fn = 1 - row1[2]
            comp.fp = row1[2]
    return comp

# calculate score
def scoring(csv_file, matching_restaurant: dict) -> float:
    data_file = pd.read_csv(filepath_or_buffer=csv_file, delimiter=',', skiprows=range(0, 5))

    cla = Classification()
    # difference of true values between two data set

    df_gold = data_file[data_file['gold'] == 1]
    print(f"labeled_data len: {len(data_file['gold'])}, own len: {len(matching_restaurant['gold'])}")
    print(f"labeled_data gold: {len(df_gold)}, own gold: {len([x for x in matching_restaurant['gold'] if x == 1])}")
    # size of data
    for ltable, rtable, gold in zip(matching_restaurant['ltable'], matching_restaurant['rtable'], matching_restaurant['gold']):
        #print(f"values: {ltable}, {rtable}, {gold}")
        #print(f"own: {type(ltable)}, {type(data_file['ltable._id'][0])}")
        df_new = data_file[data_file['ltable._id'] == ltable]
        if not df_new.empty:
            for _, row in df_new.iterrows():
                row1 = (ltable, rtable, gold)
                row2 = (row['ltable._id'], row['rtable._id'], row['gold'])
                cla += compare_row(row1, row2)
        elif ltable not in data_file['ltable._id'].values and gold == '1':
            cla.fp += 1
        elif ltable not in data_file['ltable._id'].values and gold == '0':
            cla.fn += 1

    acc = ((cla.tp + cla.tn) / (cla.tp + cla.tn + cla.fp + cla.fn)) * 100

    print("Accuracy: ", str(acc))

    print("TP: " + str(cla.tp))
    print("TN: " + str(cla.tn))
    print("FP: " + str(cla.fp))
    print("FN: " + str(cla.fn))
    #print("difference_data_size: " + str(difference_data_size))
    return acc
            
    # size of data
    for i in range(0, len(matching_restaurant[0])):
        if matching_restaurant[0][i] in data_file['rtable._id'].values:
            df_new = data_file[data_file['rtable._id'] == matching_restaurant[0][i]]

            if not df_new.empty:
                for index, row in df_new.iterrows():
                    if row['ltable._id'] == matching_restaurant[1][i]:
                        if row['gold'] == matching_restaurant[2][i]:
                            if row['gold'] == 1:
                                tp += 1
                                true_same += 1
                            else:
                                tn += 1

                        if row['gold'] != matching_restaurant[2][i]:
                            if row['gold'] == 1:
                                fn += 1
                            else:
                                fp += 1

                    elif row['ltable._id'] != matching_restaurant[1][i] and matching_restaurant[2][i] == 1:
                        tp += 1

                    elif row['ltable._id'] != matching_restaurant[1][i] and matching_restaurant[2][i] == 0:
                        tn += 1

        elif not matching_restaurant[0][i] in data_file['rtable._id'].values and matching_restaurant[2][i] == 1:
            tp += 1
        elif not matching_restaurant[0][i] in data_file['rtable._id'].values and matching_restaurant[2][i] == 0:
            tn += 1

    if len(df_gold) > len(matching_restaurant[0]):
        difference_data_size = len(df_gold) - true_same

    acc = ((tp + tn) / (tp + tn + fp + fn + difference_data_size)) * 100

    print("Accuracy: ", str(acc))

    print("TP: " + str(tp))
    print("TN: " + str(tn))
    print("FP: " + str(fp))
    print("FN: " + str(fn))
    
    return acc


if __name__ == "__main__":
    scoring()