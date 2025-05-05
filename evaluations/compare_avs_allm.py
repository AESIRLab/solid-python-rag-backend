import pandas as pd
import os

def fix_android_file(f):
    df_rows = []
    with open(f, 'r') as file:
        all = file.read()
        rows = all.split('||||')
        for row in rows[:40]:
            texts = row.split('||')
            query, eval_time, response = texts
            if query[0] == '\n':
                query = query[1:]
            df_rows.append([query, eval_time, response, f])
    return df_rows

allm_files = [
    'android_raw_files/android_vector_base_2pagequestions.csv',
    'android_raw_files/android_vector_base_4pagequestions.csv',
    'android_raw_files/android_vector_base_6pagequestions.csv'
]

avs_files = [
    'android_raw_files/android_vector_sentence_split_2pagequestions.csv',
    'android_raw_files/android_vector_sentence_split_4pagequestions.csv',
    'android_raw_files/android_vector_sentence_split_6pagequestions.csv'
]


for r1, r2 in list(zip(avs_files, allm_files)):
    avs = fix_android_file(r1)
    allm = fix_android_file(r2)
    for i1, i2 in list(zip(avs, allm)):
        if i1[2] != i2[2]:
            print("found one")