import pandas as pd

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
in_folder = 'raw_avs_responses/'
out_folder = 'formatted_avs_responses/'
files = [
    'avs_2p.csv',
    'avs_4p.csv',
    'avs_6p.csv'
]

avs_out_file = out_folder+'all_avs.csv'
dfs = []
for file in files:
    df = fix_android_csvs(in_folder+file)
    df.to_csv(out_folder+file, index=None)
    dfs.append(df)

new_df = pd.concat(dfs)
new_df.to_csv(avs_out_file)

allm_file = "./merged_responses/plain_android_gemmas.csv"

basal_df = pd.read_csv('./merged_responses/plain_gemmas.csv')
basal_df = basal_df[['query', 'reference_answer', 'reference_contexts']]
basal_df = basal_df.set_index('query')

df1 = pd.read_csv(allm_file)

df1['source_file'] = allm_file
new_df['source_file'] = avs_out_file

df1 = df1.set_index('query')
df2 = new_df.set_index('query')

left, right = 'allm', 'avs'

combined_df = df1.join(df2, how='inner', rsuffix='_r')
response_cols = list(filter(lambda x: "response" in x, combined_df.columns.values))

combined_df["left"] = left
combined_df["right"] = right
combined_df["left_answer"] = combined_df[response_cols[0]]
combined_df["right_answer"] = combined_df[response_cols[1]]
# print(combined_df.columns)
# combined_df = new_df.loc[:, ~combined_df.columns.str.contains('^Unnamed')]
reset_index = False
if 'reference_answer' not in new_df.columns.values:
    ra_df = basal_df[['reference_answer']]
    combined_df = combined_df.join(ra_df, how='inner')
    reset_index = True
    
if 'reference_contexts' not in combined_df.columns.values:
    rc_df = basal_df[['reference_contexts']]
    combined_df = combined_df.join(rc_df, how='inner')
#     new_df = new_df.reset_index()
    reset_index = True
if reset_index:
    combined_df = combined_df.reset_index()
print(combined_df.shape)
# print(df1.shape, df2.shape, new_df.shape, experiment["output_file"])
combined_df.to_csv('allm_vs_avs_fixed/allm_vs_avs_fixed.csv')

