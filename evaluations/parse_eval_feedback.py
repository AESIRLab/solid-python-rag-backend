import pandas as pd
import os
import re

folder = 'avs_dyn_qwen_results/'
bad_grades = []
bad_parse_scores = []
def parse_template(x):
    return x.split('</think>')[1]

def parse_letter_grade(x: str):
    if len(x.split('||')) < 3:
        bad_grades.append(x)
        return 'F'
    v = x.split('||')[1].strip("'")
    return v

def parse_scores(x):
    scores = [float(match) for match in re.findall(r"\d+\.?\d+", x)]
    scores = list(filter(lambda x: x <= 1.0 and x >= 0.0, scores))
    if len(scores) != 2:
        bad_parse_scores.append(x)
        return [-99, -99]
    assert len(scores) == 2
    return scores

def parse_first_response_score(x):
    return parse_scores(x)[0]

def parse_second_response_score(x):
    return parse_scores(x)[1]

for file in os.listdir(folder):
    print(file)
    if 'log_failed' in file:
        continue
# file = 'allm_vs_avs_qwen_results/qwen3_results.csv'
    df = pd.read_csv(folder+file)
    df = df.drop(df.columns[0], axis=1)
    parsed_feedback = df['feedback'].apply(parse_template)
    df['parsed_feedback'] = parsed_feedback
    df['chosen'] = df['parsed_feedback'].apply(parse_letter_grade)
    # print(file, df['chosen'].value_counts())
    df['score_left'] = df['parsed_feedback'].apply(parse_first_response_score)
    df['score_right'] = df['parsed_feedback'].apply(parse_second_response_score)
    print(df[['score_left', 'score_right']].head(10))
    assert df['score_left'].isna().any() == False 
    assert df['score_right'].isna().any() == False
    df.to_csv(f'avs_dyn_parsed_results/{file}', index=None)

    print(len(bad_parse_scores), len(bad_grades))
    