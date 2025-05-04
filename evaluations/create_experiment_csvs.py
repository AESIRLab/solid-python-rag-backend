import os
import pandas as pd

folder = "./responses/"

plain_gemmas = []
property_graph_gemmas = []
property_graph_dynamic_index_gemmas = []
vector_store_gemmas = []
vector_store_dynamic_index_gemmas = []
plain_android_gemmas = []
android_gemmas = []
android_dynamic_index_gemmas = []

def fix_vector_store_frames(files_list, location):
    gemmas_df = pd.DataFrame()
    for csv in files_list:
        df = pd.read_csv(csv, index_col=None)
        df = df.drop([df.columns[0]], axis=1)
        gemmas_df = pd.concat([gemmas_df, df], axis=0)
    gemmas_df.to_csv(location, index=False)

def concat_frames(files_list, location):
    gemmas_df = pd.DataFrame()
    for csv in files_list:
        df = pd.read_csv(csv, index_col=None)
        df = df.drop([df.columns[0], df.columns[1]], axis=1)
        gemmas_df = pd.concat([gemmas_df, df], axis=0)
    gemmas_df.to_csv(location, index=False)

def fix_android_csvs(f, location):
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
    df.to_csv(location, index=False)

def concat_android_frames(files_list, location):
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
    print(len(set(df["query"])), location)
    df.to_csv(location, index=False)
                

for file in os.listdir(folder):
    if "plain_gemma" in file:
        plain_gemmas.append(folder+file)
    elif "property_graph_gemma" in file and "plus" in file:
        property_graph_dynamic_index_gemmas.append(folder+file)
    elif "property_graph_gemma" in file:
        property_graph_gemmas.append(folder+file)
    elif "vector_store_gemma" in file and "plus" in file:
        vector_store_dynamic_index_gemmas.append(folder+file)
    elif "vector_store_gemma" in file:
        vector_store_gemmas.append(folder+file)
    elif "android_vector" in file and "plus" in file:
        android_dynamic_index_gemmas.append(folder+file)
    elif "android_vector" in file and "base" in file:
        plain_android_gemmas.append(folder+file)
    else:
        android_gemmas.append(folder+file)

dataframes = [
    "./merged_responses/plain_gemmas.csv",
    "./merged_responses/property_graph_gemmas.csv",
    "./merged_responses/vector_store_gemmas.csv",
    "./merged_responses/property_graph_dyn_idx_gemmas.csv",
    "./merged_responses/vector_store_dyn_idx_gemmas.csv",
    "./merged_responses/android_store_gemmas.csv",
    "./merged_responses/android_store_dyn_idx_gemmas.csv",
    "./merged_responses/plain_android_gemmas.csv"
]

adig_names = iter(['avs_2p2p2.csv', 'avs_4p2.csv', 'avs_2p2.csv'])
for file in android_dynamic_index_gemmas:
    location = f'./android_csvs/{next(adig_names)}'
    fix_android_csvs(file, location)

ag_names = iter(['avs_4.csv', 'avs_2.csv',  'avs_6.csv'])
for file in android_gemmas:
    location = f'./android_csvs/{next(ag_names)}'
    print(file)
    fix_android_csvs(file, location)

pag_names = iter(['allm_4.csv', 'allm_2.csv', 'allm_6.csv'])
for file in plain_android_gemmas:
    location = f'./android_csvs/{next(pag_names)}'
    print(file)
    fix_android_csvs(file, location)


concat_frames(plain_gemmas, dataframes[0])
concat_frames(property_graph_gemmas, dataframes[1])
fix_vector_store_frames(vector_store_gemmas, dataframes[2])
concat_frames(property_graph_dynamic_index_gemmas, dataframes[3])
fix_vector_store_frames(vector_store_dynamic_index_gemmas, dataframes[4])

concat_android_frames(android_gemmas, dataframes[5])
concat_android_frames(android_dynamic_index_gemmas, dataframes[6])
concat_android_frames(plain_android_gemmas, dataframes[7])
