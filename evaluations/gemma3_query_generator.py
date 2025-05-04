import nest_asyncio

nest_asyncio.apply()

import wikipedia
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
from llama_index.core import Settings
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.schema import Document
from llama_index.llms.huggingface import HuggingFaceLLM
import os
HF_TOKEN = os.getenv("HF_TOKEN_PATH")

gemma = HuggingFaceLLM(model_name="google/gemma-3-1b-it", tokenizer_name="google/gemma-3-1b-it")
Settings.llm = gemma
Settings.chunk_size = 1024
Settings.chunk_overlap = 128

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

question_gen_prompt = """\
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge.
generate only questions based on the below query. 
Only provide the generated question, do not respond with anything else.
{query_str}
"""

for page in wikipedia_pages:
    documents = reader.load_data([page])
    dataset_generator = RagDatasetGenerator.from_documents(
        documents, show_progress=True, 
        workers=16, num_questions_per_chunk=3,
        text_question_template=PromptTemplate(question_gen_prompt)
        )
    dataset = dataset_generator.generate_dataset_from_nodes()
    
    df = dataset.to_pandas()
    df.to_csv(f'./data/{page}_gemma.csv')


for page_num in range(2, len(wikipedia_pages)+1, 2):
    pages_set = wikipedia_pages[:page_num]
    pages_content = []
    for page in pages_set:
        wiki_page = wikipedia.page(page)
        pages_content.append(wiki_page.content)
    page_content = "\n".join(pages_content)
    documents = [Document(id_=str(page_num), text=page_content)]
    
    dataset_generator = RagDatasetGenerator.from_documents(
        documents, show_progress=True, 
        workers=16, num_questions_per_chunk=3,
        text_question_template=PromptTemplate(question_gen_prompt)
        )
    dataset = dataset_generator.generate_dataset_from_nodes()
    
    df = dataset.to_pandas()
    df.to_csv(f'./data/{page_num}_gemma_wiki_pages.csv')
