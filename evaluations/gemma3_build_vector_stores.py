from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
import time
import nest_asyncio
import os
import asyncio
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


gemma = HuggingFaceLLM(model_name="google/gemma-3-1b-it", tokenizer_name="google/gemma-3-1b-it")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3", max_length=1024)
Settings.embed_model = embed_model
Settings.llm = gemma
Settings.chunk_size = 1024
Settings.chunk_overlap = 128

async def main():
        index_creation_times = []

        for pages in range(2, len(wikipedia_pages) + 1, 2):
            documents = reader.load_data(wikipedia_pages[:pages])
            print(f"documents loaded: {wikipedia_pages[:pages]}")
            index_creation_start_time = time.time()
            index = VectorStoreIndex.from_documents(
                use_async=True,
                show_progress=True,
                documents=documents
            )
            index.storage_context.persist(f"./inmemory_vector_stores/gemma3_vector_store_{pages}_pages/")

            index_creation_total_time = time.time() - index_creation_start_time
            index_creation_times.append(index_creation_total_time)
        print(f"all index creation times: {index_creation_times}")
    
if __name__ == '__main__':
    asyncio.run(main())