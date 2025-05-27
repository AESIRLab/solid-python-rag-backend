import pandas as pd

experiments = [
    {
        "file1": "./android_experiments/avs_4p.csv",
        "file2": "./android_experiments/avs_2p2_memorize.csv",
        "output_file": "./android_dyn_experiment_frames/avs4_v_avs2p2.csv",
    },
    {
        "file1": "./android_experiments/avs_6p.csv",
        "file2": "./android_experiments/avs_2p2p2_memorize.csv",
        "output_file": "./android_dyn_experiment_frames/avs6_v_avs2p2p2.csv",
    },
    {
        "file1": "./android_experiments/avs_6p.csv",
        "file2": "./android_experiments/avs_4p2_memorize.csv",
        "output_file": "./android_dyn_experiment_frames/avs6_v_avs4p2.csv",
    },
    {
        "file1": "./android_experiments/avs_4p2_memorize.csv",
        "file2": "./android_experiments/avs_2p2p2_memorize.csv",
        "output_file": "./android_dyn_experiment_frames/avs4p2_v_avs2p2p2.csv",
    },
    {
        "file1": "./formatted_avs_responses/all_avs.csv",
        "file2": "./merged_responses/property_graph_gemmas.csv",
        "output_file": "./android_dyn_experiment_frames/avs_v_pg.csv"
    },
    {
        "file1": "./formatted_avs_responses/all_avs.csv",
        "file2": "./merged_responses/vector_store_gemmas.csv",
        "output_file": "./android_dyn_experiment_frames/avs_v_vs.csv"
    },

]

basal_df = pd.read_csv('./merged_responses/plain_gemmas.csv')
basal_df = basal_df[['query', 'reference_answer', 'reference_contexts']]
basal_df = basal_df.set_index('query')
# print(basal_df.head())
for experiment in experiments:
    df1 = pd.read_csv(experiment["file1"])
    df2 = pd.read_csv(experiment["file2"])
    
    df1['source_file'] = experiment["file1"]
    df2['source_file'] = experiment["file2"]
    
    df1 = df1.set_index('query')
    df2 = df2.set_index('query')

    left, right = experiment["output_file"].rsplit("/", 1)[1].replace(".csv", "").split("_v_")
    
    new_df = df1.join(df2, how='inner', rsuffix='_r')
    response_cols = list(filter(lambda x: "response" in x, new_df.columns.values))
    new_df["left"] = left
    new_df["right"] = right
    new_df["left_answer"] = new_df[response_cols[0]]
    new_df["right_answer"] = new_df[response_cols[1]]
    new_df = new_df.loc[:, ~new_df.columns.str.contains('^Unnamed')]
    reset_index = False
    if 'reference_answer' not in new_df.columns.values:
        ra_df = basal_df[['reference_answer']]
        new_df = new_df.join(basal_df, how='inner')
        reset_index = True
        
    if 'reference_contexts' not in new_df.columns.values:
        rc_df = basal_df[['reference_contexts']]
        new_df = new_df.join(rc_df, how='inner')
    #     new_df = new_df.reset_index()
        reset_index = True
    if reset_index:
        new_df = new_df.reset_index()
    print(df1.shape, df2.shape, new_df.shape, experiment["output_file"])
    new_df.to_csv(experiment["output_file"])