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

def concat_android_frames(files_list):
    df_rows = []
    for f in files_list:
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
    # print(len(set(df["query"])), location)
    return df

dyn_avs_folder = 'dyn_avs_responses/'
dyn_avs_files = [
    'avs_2p2_memorize.csv',
    'avs_2p2p2_memorize.csv',
    'avs_4p2_memorize.csv',
]

plain_avs_folder = 'raw_avs_responses/'
plain_avs_files = [
    'avs_2p.csv',
    'avs_4p.csv',
    'avs_6p.csv',
]
# allm_file = "./merged_responses/plain_android_gemmas.csv"

# plain_android_gemmas = []
android_gemma_dfs = []
android_dynamic_index_dfs = []

out_folder = 'android_experiments/'
for file in dyn_avs_files:
    df = fix_android_csvs(dyn_avs_folder+file)
    df.to_csv(out_folder+file,index=False)
    # android_dynamic_index_dfs.append(df)

for file in plain_avs_files:
    df = fix_android_csvs(plain_avs_folder+file)
    df.to_csv(out_folder+file, index=False)
    # android_gemma_dfs.append(df)

# merged_out_folder = 'android_merged_responses/'
# all_static_android_df = pd.concat(android_gemma_dfs)
# all_static_android_df.to_csv(merged_out_folder+'android_store_gemmas.csv', index=False)
# all_dynamic_android_df = pd.concat(android_dynamic_index_dfs+'dynamic_')
# all_dynamic_android_df.to_csv(merged_out_folder+'', index=False)