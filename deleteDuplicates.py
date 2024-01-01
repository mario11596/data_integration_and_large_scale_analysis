from __future__ import annotations
import numpy as np
import os
import pandas as pd


def delete_duplicates(id_list: list, csv_file: os.PathLike):

    dropped_amount = 0
    df = pd.read_csv(csv_file, delimiter=',', low_memory=False)
    for id in id_list:
        dropped_amount += 1
        idx = df[df['ID'] == id].index
        df = df.drop(idx, axis=0)
    
    print(f"Deleted Duplicates in {csv_file} is {dropped_amount}")
    df.to_csv(csv_file, index=False, sep=',')


def get_average_entries_per_block(blocking: dict) -> int:
    amount_list = []
    for _, values in blocking.items():
        amount_list.append(len(values))
    
    return np.mean(np.array(amount_list))