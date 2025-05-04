from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core import Settings
import time
import nest_asyncio
import os
import asyncio
import pandas as pd
HF_TOKEN = os.getenv("HF_TOKEN_PATH")

runtime_start = time.time()
nest_asyncio.apply()

reader = WikipediaReader()

wikipedia_pages = [
    'Charles_Darwin',
    'Westminster_Abbey',
    'University_of_Edinburgh',
    'Emma_Darwin',
    'Geological_Society_of_London',
    'John_Stevens_Henslow',
    'Adam_Sedgwick',
    'The_Voyage_of_the_Beagle',
    'Copley_Medal',
    'On_the_Origin_of_Species',
]

gemma = HuggingFaceLLM(model_name="google/gemma-3-1b-it", tokenizer_name="google/gemma-3-1b-it")
Settings.llm = gemma
Settings.chunk_size = 1024
Settings.chunk_overlap = 128

async def main():
    experiments = [
        {
            "filename": "./selected_queries/two_page_questions_queries.csv"
        },
        {
            "filename": "./selected_queries/four_page_questions_queries.csv"
        },
        {
            "filename": "./selected_queries/six_page_questions_queries.csv"
        },
    ]
    for experiment in experiments:
        df = pd.read_csv(experiment["filename"])
        # print(df.columns)
        responses = []
        query_eval_times = []
        for query in df["query"].to_numpy():
            start_time = time.time()
            response = gemma.complete(query)
            responses.append(response)
            resp_time = time.time() - start_time
            query_eval_times.append(resp_time)
            print(f"evaluated: {query} in {resp_time} seconds")
        df["plain_gemma_responses"] = responses
        df["plain_gemma_query_eval_time (s)"] = query_eval_times
        new_filename = "plain_gemma_" + experiment["filename"].rsplit("/", 1)[1]
        print(f"saved file at ./responses/{new_filename}")
        df.to_csv(f"./responses/{new_filename}")

if __name__ == '__main__':
    asyncio.run(main())