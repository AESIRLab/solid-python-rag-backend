from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core import Settings
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
from llama_index.core import PropertyGraphIndex
import time
import nest_asyncio
import os
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
Settings.llm = gemma
Settings.chunk_size = 1024
Settings.chunk_overlap = 128

username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
url = os.getenv("NEO4J_URL")

kg_extractor = SimpleLLMPathExtractor(
    llm=Settings.llm,
    max_paths_per_chunk=32,
    num_workers=16,
)

databases = iter(["twopagesgemma", "fourpagesgemma", "sixpagesgemma", ])# "eightpagesgemma", "tenpagesgemma"])

for i in range(2, len(wikipedia_pages) + 1, 2):
    docs = wikipedia_pages[:i]
    database_name = next(databases)
    documents = reader.load_data(docs)

    graph_store = Neo4jPropertyGraphStore(
        url=url,
        username=username,
        password=password,
        database=database_name
    )

    index = PropertyGraphIndex.from_documents(
        documents=documents,
        property_graph_store=graph_store,
        kg_extractors=[
            kg_extractor,
        ],
        show_progress=True,
        max_triplets_per_chunk=16,
        embed_kg_nodes=False,
    )
    print(f"finished doc set: {docs} for database {database_name}")
