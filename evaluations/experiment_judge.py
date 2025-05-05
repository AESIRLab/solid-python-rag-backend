

# attach to the same event-loop
import nest_asyncio
import asyncio
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.evaluation import PairwiseComparisonEvaluator
from httpcore import ReadTimeout as httpCoreReadTimeout
from httpx import ReadTimeout as httpReadTimeout
import pandas as pd
import time
import os
nest_asyncio.apply()

Settings.chunk_size = 1024
Settings.chunk_overlap = 128
llm = Ollama(model="qwen3:14b", verbose=True, temperature=0.0, request_timeout=45)
Settings.llm = llm


pairwise_eval_prompt_template = "You are to perform the role as an impartial judge in determining the better reponse" + \
"between two AI-generated responses: {answer_1} and {answer_2}."+ \
"You should evaluate these responses based upon" + \
"their content, how well they answer the query: {query}, and" + \
"similarity to the provided reference answer: {reference}. For the first response, provide a score strictly between 0.0 and 1.0, and one sentence of feedback." + \
"Use this score and setence to fill in Response 1 Feedback and Response 1 Score in the output template." + \
"For the second response, provide a score strictly between 0.0 and 1.0, and one sentence of feedback." + \
"Use this score and setence to fill in Response 2 Feedback and Response 2 Score in the output template." + \
"After you have determined one score and one sentence of feedback for the first response, " + \
"and you have provided one score and one sentence of feedback for the second response, " + \
"you should provide the final choice of the better response between the responses. " + \
"If the first response is better, then output 'A' in the response template." + \
"If the second response is better, then output 'B' in the response template. " + \
"If the first and second response scores are equal, then output 'C' in the response template. " + \
"Be as unbiased and impartial as possible to the phrasing of the queries. " + \
"You should always only provide one feedback template in the response. " + \
"You should always provide your final output strictly according to the following template: " + \
"### [[Response 1 Feedback]] **Response 1 Score** [[Response 2 Feedback]] **Response 2 Score** ||'A' or 'B' or 'C'||"

def parser_function(outputs: str):
    # parts = outputs.split("[RESULT]")
    # print(outputs)
    # if len(parts) == 2:
    #     feedback, result = parts[0].strip(), parts[1].strip()
    #     if result == "A":
    #         return True, 0.0, feedback
    #     else:
    #         return True, 1.0, feedback
    return None, None, None

completed = [
]

async def main():
    # experiment_frames = 'ctx_experiment_frames/'
    experiment_frames = 'allm_vs_avs_fixed/'
    pairwise_evaluator = PairwiseComparisonEvaluator(
        enforce_consensus=False,
        parser_function=parser_function,
        eval_template=pairwise_eval_prompt_template
    )
    log_failures = []
    for file in os.listdir(experiment_frames):
        file_start = time.time()
        if file in completed:
            print(f"skipped file in completed: {file}")
            continue
        
        df = pd.read_csv(experiment_frames+file)
        if df.columns.values[0] != 'query':
            df = df.drop(df.columns[0], axis=1)
        df = df[['query', 'reference_answer', 'reference_contexts', 'left_answer', 'right_answer', 'left', 'right']]
        queries = df['query'].to_numpy()
        contexts = df['reference_contexts'].to_numpy()
        answers = df['reference_answer'].to_numpy()
        left_responses = df['left_answer'].to_numpy()
        right_responses = df['right_answer'].to_numpy()
        lefts = df['left'].to_numpy()
        rights= df['right'].to_numpy()
        results = []
        print(len(queries))
        for idx, (query, context, answer, left_response, right_response, left, right) in enumerate(list(zip(queries, contexts, answers, left_responses, right_responses, lefts, rights))):
            eval_start = time.time()
            # print(f"left response: {left_response}\n\n")
            # print(f"right response: {right_response}\n\n")
            
            try:
                pairwise_result = await pairwise_evaluator.aevaluate(
                    query=query,
                    response=left_response,
                    # contexts=[context],
                    second_response=right_response,
                    reference=answer
                )
            except httpReadTimeout:
                print(f"log failed httpReadtimeout at query: {query} in file {file}")
                log_failures.append([query, experiment_frames+file])
                continue
            except httpCoreReadTimeout:
                print(f"log failed httpCoreReadtimeout at query: {query} in file {file}")
                log_failures.append([query, experiment_frames+file])
                continue

            # print(pairwise_result.feedback)
            print(f"time taken in seconds: {time.time() - eval_start}")
            results.append([query, left, right, 
                            pairwise_result.feedback])
            
        out_df = pd.DataFrame(results, columns=['query', 'left', 'right', 
                                                'feedback'
                                                ])
        # # out_df.to_csv(f'./qwen3_experiment_results_run2/{file.replace(".csv", "_result.csv")}')
        out_df.to_csv(f'./allm_vs_avs_qwen_results/qwen3_results.csv')
        # print(f"finished file: {file} in {time.time() - file_start}")
    log_failures_df = pd.DataFrame(log_failures, columns=['query', 'filename'])
    # log_failures_df.to_csv(f'./qwen3_experiment_results_run2/log_failed_queries.csv')
    log_failures_df.to_csv(f'./allm_vs_avs_qwen_results/log_failed_queries.csv')
    

if __name__ == '__main__':
    asyncio.run(main())