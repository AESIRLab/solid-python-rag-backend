import pandas as pd

files = [
    './query_files/two_page_questions',
    './query_files/four_page_questions',
    './query_files/six_page_questions',
    './query_files/eight_page_questions',
    './query_files/all_page_questions',
]

for file in files:
    df = pd.read_csv(file+".csv")
    file_name = file.rsplit("/", 1)
    df = df.drop(df.columns[0], axis=1)
    df = df[df["query"].str.endswith('?')]
    sampled_df = df.sample(40)
    sampled_df.to_csv(f"./selected_queries/{file_name[1]}_queries.csv")
    print(sampled_df.shape)
    with open(f"./selected_queries/{file_name[1]}_queries.txt", "w") as txt_query:
        queries = sampled_df['query'].to_numpy()
        for query in queries:
            txt_query.write(query+"\n")