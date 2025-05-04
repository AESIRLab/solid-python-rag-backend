import pandas as pd
import glob

all_csvs = glob.glob("./data/*.csv")
print(all_csvs)
dfs = []
for f in all_csvs:
    curr_df = pd.read_csv(f)
    curr_df['source'] = f
    dfs.append(curr_df)
df = pd.concat(dfs)
df = df.drop(df.columns[0], axis=1)
df.to_csv('./output/all_generated_questions.csv')
duplicated_subset = df.drop_duplicates(["query"], keep='first')
duplicated_subset.to_csv("output/duplicated_questions.csv")
unique_subset = df.drop_duplicates(["query"], keep=False)
unique_subset.to_csv("output/unique_questions.csv")
print(duplicated_subset.shape, unique_subset.shape)