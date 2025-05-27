import pandas as pd
import os

def fix_android_csvs(f):
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
    df = pd.DataFrame(df_rows, columns=['query', 'android_query_eval_time', 'android_response', 'android_src_file'])
    return df

folder = 'mem_vs_no_mem/'

no_mem = []
mem = []
for file in os.listdir(folder):
    if "no_memorize" in file:
        no_mem.append(folder+file)
    else:
        mem.append(folder+file)


for file in no_mem:
    df = fix_android_csvs(file)
    df['android_query_eval_time'] = df['android_query_eval_time'].astype('int64')
    # print(df['android_query_eval_time'].head(2))
    print(df['android_query_eval_time'].median(), df['android_query_eval_time'].mean())

for file in mem:
    df = fix_android_csvs(file)
    df['android_query_eval_time'] = df['android_query_eval_time'].astype('int64')
    # print(df['android_query_eval_time'].head(2))
    print(df['android_query_eval_time'][1:].median(), df['android_query_eval_time'][1:].mean())