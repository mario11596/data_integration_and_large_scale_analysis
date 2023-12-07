import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('config.ini')
config = config['default']
filter_file = config['filepath_raw']


# calculate score
def scoring():
    data_file = pd.read_csv(filepath_or_buffer=filter_file, delimiter=',', skiprows=range(0, 5))

    # first array is Yelp, second array is Zomato, third array is gold (matching)
    matching_restaurant = [[4, 4, 18],
           [12, 13, 4537],
           [1, 0, 0]]

    # true positive
    tp = 0
    # true negative
    tn = 0
    # false positive
    fp = 0
    # false negative
    fn = 0
    # difference of true values between two data set
    difference_data_size = 0

    true_same = 0

    df_gold = data_file[data_file['gold'] == 1]

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


if __name__ == "__main__":
    scoring()