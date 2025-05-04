from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core import Settings, StorageContext, get_response_synthesizer, load_index_from_storage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode
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
    # 'Adam_Sedgwick',
    # 'The_Voyage_of_the_Beagle',
    # 'Copley_Medal',
    # 'On_the_Origin_of_Species',
]

documents = reader.load_data(wikipedia_pages)

gemma = HuggingFaceLLM(model_name="google/gemma-3-1b-it", tokenizer_name="google/gemma-3-1b-it")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3", max_length=1024)
Settings.embed_model = embed_model
Settings.llm = gemma
Settings.chunk_size = 1024
Settings.chunk_overlap = 128

async def main():
    experiments = [
        {
            "queries_file": "./selected_queries/two_page_questions_queries.csv",
            "storage_dir": "./inmemory_vector_stores/gemma3_vector_store_2_pages/",
            "output_file_name": "./responses/vector_store_gemma_two_pages_questions_queries.csv",
            "add_documents": None,
        },
        {
            "queries_file": "./selected_queries/four_page_questions_queries.csv",
            "storage_dir": "./inmemory_vector_stores/gemma3_vector_store_4_pages/",
            "output_file_name": "./responses/vector_store_gemma_four_pages_questions_queries.csv",
            "add_documents": None,
        },
        {
            "queries_file": "./selected_queries/six_page_questions_queries.csv",
            "storage_dir": "./inmemory_vector_stores/gemma3_vector_store_6_pages/",
            "output_file_name": "./responses/vector_store_gemma_six_pages_questions_queries.csv",
            "add_documents": None,
        },
        {
            "queries_file": "./selected_queries/four_page_questions_queries.csv",
            "storage_dir": "./inmemory_vector_stores/gemma3_vector_store_2_plus_2_pages/",
            "output_file_name": "./responses/vector_store_gemma_two_plus_two_pages_questions_queries.csv",
            "add_documents": documents[2:4],
        },
        {
            "queries_file": "./selected_queries/six_page_questions_queries.csv",
            "storage_dir": "./inmemory_vector_stores/gemma3_vector_store_4_plus_2_pages/",
            "output_file_name": "./responses/vector_store_gemma_four_plus_two_pages_questions_queries.csv",
            "add_documents": documents[4:6],
        },
        {
            "queries_file": "./selected_queries/six_page_questions_queries.csv",
            "storage_dir": "./inmemory_vector_stores/gemma3_vector_store_2_plus_2_plus_2_pages/",
            "output_file_name": "./responses/vector_store_gemma_two_plus_two_plus_two_pages_questions_queries.csv",
            "add_documents": documents[2:6],
        },
    ]

    for experiment in experiments:
        df = pd.read_csv(experiment["queries_file"])
        responses = []
        query_eval_times = []
        index_creation_times = []

        index_creation_start_time = time.time()
        storage_context = StorageContext.from_defaults(persist_dir=experiment["storage_dir"])
        index = load_index_from_storage(storage_context)
        if experiment["add_documents"] is not None:
            for document in experiment["add_documents"]:
                index.insert(document)
        index_creation_total_time = time.time() - index_creation_start_time
        retriever = index.as_retriever()

        response_sythensizer = get_response_synthesizer(
            response_mode=ResponseMode.COMPACT,
            use_async=True
        )

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_sythensizer,
        )

        for query in df["query"].to_numpy():
            start_time = time.time()
            response = query_engine.query(query)
            responses.append(response)
            resp_time = time.time() - start_time
            query_eval_times.append(resp_time)
            index_creation_times.append(index_creation_total_time)
            print(f"evaluated: {query} in {resp_time} seconds")
        df["vector_store_gemma_responses"] = responses
        df["vector_store_gemma_query_eval_time (s)"] = query_eval_times
        new_filename = experiment['output_file_name']
        print(f"saved file at {new_filename}")
        print(f"index creation times for file {new_filename}: {index_creation_times}")
        df.to_csv(new_filename)

if __name__ == '__main__':
    asyncio.run(main())