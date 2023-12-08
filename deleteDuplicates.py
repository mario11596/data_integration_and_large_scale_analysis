#delete_duplicates(ids1, outputfile1) -> outputfile1
#delete_duplicates(ids2, outputfile2) -> outputfile2

from __future__ import annotations
import numpy as np
import pandas as pd

#def delete_duplicates(id_list, inputdf) -> pd.Dataframe:
def delete_duplicates(id_list: list, csv_file):
    #df = inputdf.copy(deep=True)
    dropped_amount = 0
    df = pd.read_csv(csv_file, delimiter=',', low_memory=False)
    for id in id_list:
        dropped_amount += 1
        idx = df[df['ID'] == id].index
        df = df.drop(idx, axis=0)
    
    print(f"Deleted Duplicates {dropped_amount}")
    df.to_csv(csv_file, index=False, sep=',')
    #return df

#TODO add to blocking and call for extra info
def get_average_entries_per_block(blocking: dict) -> int:
    amount_list = []
    for _, values in blocking.items():
        amount_list.append(len(values))
    
    return np.mean(np.array(amount_list))