import os
import pandas as pd
from pandas import DataFrame

folder = "./responses/"

plain_gemmas = []
property_graph_gemmas = []
property_graph_dynamic_index_gemmas = []
vector_store_gemmas = []
vector_store_dynamic_index_gemmas = []
plain_android_gemmas = []
android_gemmas = []
android_dynamic_index_gemmas = []

def concat_vector_store_frames(files_list) -> list[DataFrame]:
    frames = []
    for csv in files_list:
        df = pd.read_csv(csv, index_col=None)
        df = df.drop([df.columns[0]], axis=1)
        df['source_file'] = csv
        frames.append(df)
    return frames

def concat_frames(files_list) -> list[DataFrame]:
    frames = []
    for csv in files_list:
        df = pd.read_csv(csv, index_col=None)
        df = df.drop([df.columns[0], df.columns[1]], axis=1)
        df['source_file'] = csv
        frames.append(df)
    return frames

def concat_android_frames(files_list) -> list[DataFrame]:
    frames = []
    for f in files_list:
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
        df = pd.DataFrame(df_rows, columns=['query', 'eval_time (s)', 'response', 'source_file'])
        frames.append(df)
    return frames
                

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

all_frames: list[DataFrame] = []
all_frames += concat_frames(plain_gemmas)
all_frames += concat_frames(property_graph_gemmas)
all_frames += concat_vector_store_frames(vector_store_gemmas)
all_frames += concat_frames(property_graph_dynamic_index_gemmas)
all_frames += concat_vector_store_frames(vector_store_dynamic_index_gemmas)

all_frames += concat_android_frames(android_gemmas)
all_frames += concat_android_frames(android_dynamic_index_gemmas)
all_frames += concat_android_frames(plain_android_gemmas)

source_files = {
    './responses/android_vector_sentence_split_4pagequestions.csv': [4, 'avs'],
    './responses/property_graph_gemma_two_plus_two_plus_two_pages_questions_queries.csv': [6, 'pg2p2p2'],
    './responses/vector_store_gemma_two_plus_two_plus_two_pages_questions_queries.csv': [6, 'vs2p2p2'],
    './responses/android_vector_sentence_split_2pagequestions.csv': [2, 'avs'],
    './responses/vector_store_gemma_four_pages_questions_queries.csv': [4, 'vs'],
    './responses/android_vector_sentence_split_2_plus_2_plus_2pagequestions.csv': [6, 'avs2p2p2'],
    './responses/property_graph_gemma_two_pages_questions_queries.csv': [2, 'pg'],
    './responses/plain_gemma_four_page_questions_queries.csv': [4, 'llm'],
    './responses/android_vector_base_4pagequestions.csv': [4, 'allm'],
    './responses/android_vector_sentence_split_4_plus_2pagequestions.csv': [6, 'avs4p2'],
    './responses/property_graph_gemma_four_plus_two_pages_questions_queries.csv': [6, 'pg4v2'],
    './responses/plain_gemma_two_page_questions_queries.csv': [2, 'llm'],
    './responses/vector_store_gemma_six_pages_questions_queries.csv': [6, 'vs'],
    './responses/property_graph_gemma_six_pages_questions_queries.csv': [6, 'pg'],
    './responses/android_vector_base_2pagequestions.csv': [2, 'allm'],
    './responses/android_vector_sentence_split_2_plus_2pagequestions.csv': [4, 'avs2p2'],
    './responses/android_vector_base_6pagequestions.csv': [6, 'allm'],
    './responses/plain_gemma_six_page_questions_queries.csv': [6, 'llm'],
    './responses/vector_store_gemma_four_plus_two_pages_questions_queries.csv': [6, 'vs4p2'],
    './responses/property_graph_gemma_two_plus_two_pages_questions_queries.csv': [4, 'pg2p2'],
    './responses/vector_store_gemma_two_plus_two_pages_questions_queries.csv': [4, 'vs2p2'],
    './responses/property_graph_gemma_four_pages_questions_queries.csv': [4, 'pg'],
    './responses/android_vector_sentence_split_6pagequestions.csv': [6, 'avs'],
    './responses/vector_store_gemma_two_pages_questions_queries.csv': [2, 'vs']
    }

def lookup_src_file(x):
    query_pool, group_identifier = source_files[x]
    return query_pool, group_identifier

def get_query_pool(x):
    return str(lookup_src_file(x)[0])

def get_group_id(x):
    return lookup_src_file(x)[1]

new_frames = []
for frame in all_frames:
    frame = frame.rename(columns={'android_src_file': 'source', 
                                  'vector_store_gemma_query_eval_time (s)': 'eval_time (s)',
                                  'vector_store_gemma_responses': 'response',
                                  'property_graph_gemma_responses': 'response',
                                  'property_graph_gemma_query_eval_time (s)': 'eval_time (s)',
                                  'plain_gemma_responses': 'response',
                                  'plain_gemma_query_eval_time (s)': 'eval_time (s)'})
    frame['query_pool'] = frame['source_file'].apply(get_query_pool)
    frame['group_id'] = frame['source_file'].apply(get_group_id)
    new_frames.append(frame)

total_df = pd.concat(new_frames, ignore_index=True)
total_df.to_csv('test_all_queries.csv')