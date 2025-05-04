import pandas as pd

experiments = [
    {
        "file1": "./merged_responses/plain_gemmas.csv",
        "file2": "./merged_responses/vector_store_gemmas.csv",
        "output_file": "./ctx_experiment_frames/llm_v_vs.csv",
    },
    {
        "file1": "./merged_responses/plain_android_gemmas.csv",
        "file2": "./merged_responses/android_store_gemmas.csv",
        "output_file": "./ctx_experiment_frames/allm_v_avs.csv",
    },
    {
        "file1": "./merged_responses/plain_gemmas.csv",
        "file2": "./merged_responses/property_graph_gemmas.csv",
        "output_file": "./ctx_experiment_frames/llm_v_pg.csv",
    },
    {
        "file1": "./merged_responses/plain_android_gemmas.csv",
        "file2": "./merged_responses/plain_gemmas.csv",
        "output_file": "./ctx_experiment_frames/allm_v_llm.csv",
    },
    {
        "file1": "./merged_responses/android_store_gemmas.csv",
        "file2": "./merged_responses/vector_store_gemmas.csv",
        "output_file": "./ctx_experiment_frames/avs_v_vs.csv",
    },
    {
        "file1": "./merged_responses/property_graph_gemmas.csv",
        "file2": "./merged_responses/vector_store_gemmas.csv",
        "output_file": "./ctx_experiment_frames/pg_v_vs.csv",
    },
    ### 120 v 120 above here ###############
    ### AVS DYNAMIC COMPARISONS BELOW ##############
    {
        "file1": "./android_csvs/avs_4.csv",
        "file2": "./android_csvs/avs_2p2.csv",
        "output_file": "./ctx_experiment_frames/avs4_v_avs2p2.csv",
    },
    {
        "file1": "./android_csvs/avs_6.csv",
        "file2": "./android_csvs/avs_2p2p2.csv",
        "output_file": "./ctx_experiment_frames/avs6_v_avs2p2p2.csv",
    },
    {
        "file1": "./android_csvs/avs_6.csv",
        "file2": "./android_csvs/avs_4p2.csv",
        "output_file": "./ctx_experiment_frames/avs6_v_avs4p2.csv",
    },
    {
        "file1": "./android_csvs/avs_4p2.csv",
        "file2": "./android_csvs/avs_2p2p2.csv",
        "output_file": "./ctx_experiment_frames/avs4p2_v_avs2p2p2.csv",
    },
    ### AVS DYNAMIC COMPARISONS ABOVE ##############
    ### LOCAL DYNAMIC VS COMPARISONS BELOW #########
    {
        "file1": "./responses/vector_store_gemma_four_pages_questions_queries.csv",
        "file2": "./responses/vector_store_gemma_two_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/vs4_v_vs2p2.csv",
    },
    {
        "file1": "./responses/vector_store_gemma_six_pages_questions_queries.csv",
        "file2": "./responses/vector_store_gemma_four_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/vs6_v_vs4p2.csv",
    },
    {
        "file1": "./responses/vector_store_gemma_six_pages_questions_queries.csv",
        "file2": "./responses/vector_store_gemma_two_plus_two_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/vs6_v_vs2p2p2.csv",
    },
    {
        "file1": "./responses/vector_store_gemma_four_plus_two_pages_questions_queries.csv",
        "file2": "./responses/vector_store_gemma_two_plus_two_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/vs4p2_v_vs2p2p2.csv",
    },
    ### LOCAL DYNAMIC VS COMPARISONS ABOVE ########
    ### LOCAL DYNAMIC PROPERTY GRAPH COMPARISONS BELOW ############
    {
        "file1": "./responses/property_graph_gemma_four_pages_questions_queries.csv",
        "file2": "./responses/property_graph_gemma_two_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/pg4_v_pg2p2.csv",
    },
    {
        "file1": "./responses/property_graph_gemma_six_pages_questions_queries.csv",
        "file2": "./responses/property_graph_gemma_four_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/pg6_v_pg4p2.csv",
    },
    {
        "file1": "./responses/property_graph_gemma_six_pages_questions_queries.csv",
        "file2": "./responses/property_graph_gemma_two_plus_two_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/pg6_v_pg2p2p2.csv",
    },
    {
        "file1": "./responses/property_graph_gemma_four_plus_two_pages_questions_queries.csv",
        "file2": "./responses/property_graph_gemma_two_plus_two_plus_two_pages_questions_queries.csv",
        "output_file": "./ctx_experiment_frames/pg4p2_v_pg2p2p2.csv",
    },
    ### LOCAL DYNAMIC PROPERTY GRAPH COMPARISONS ABOVE ################
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