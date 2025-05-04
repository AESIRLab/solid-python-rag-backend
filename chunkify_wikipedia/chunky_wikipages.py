import wikipedia
import spacy
import nltk

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document

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

nlp = spacy.load("en_core_web_sm")
nltk.download('punkt')

for page in wikipedia_pages:
    wiki_page = wikipedia.page(page)
    
    doc = nlp(wiki_page.content)
    spacy_sentences = [sent.text for sent in doc.sents]
    spacy_chunk_string = "<ch_s>".join(spacy_sentences)
    with open(f"./spacy_sentences/{page}.txt", "w") as file:
        file.write(spacy_chunk_string)
    
    nltk_sentences = nltk.sent_tokenize(wiki_page.content)
    nltk_chunk_string = "<ch_s>".join(nltk_sentences)
    with open(f"./nltk_sentences/{page}.txt", "w") as file:
        file.write(nltk_chunk_string)

    document = Document(id_=wiki_page.pageid, text=wiki_page.content)

    sentence_splitter = SentenceSplitter(separator=".", chunk_size=1024, chunk_overlap=128)
    nodes = sentence_splitter.get_nodes_from_documents([document], show_progress=True)
    nodes_chunk_string = "<ch_s>".join((node.get_content() for node in nodes))
    with open(f"./sentence_split_sentences/{page}.txt", "w") as file:
        file.write(nodes_chunk_string)

for page_num in range(2, len(wikipedia_pages) + 1, 2):
    print(page_num)
    pages_set = wikipedia_pages[:page_num]
    pages_content = []
    for page in pages_set:
        wiki_page = wikipedia.page(page)
        pages_content.append(wiki_page.content)
    page_content = "\n".join(pages_content)
    documents = [Document(id_=str(page_num), text=page_content)]

    doc = nlp(page_content)
    spacy_sentences = [sent.text for sent in doc.sents]
    spacy_chunk_string = "<ch_s>".join(spacy_sentences)
    with open(f"./folded_documents/spacy_{page_num}pages.txt", "w") as file:
        file.write(spacy_chunk_string)
    
    nltk_sentences = nltk.sent_tokenize(page_content)
    nltk_chunk_string = "<ch_s>".join(nltk_sentences)
    with open(f"./folded_documents/nltk_{page_num}pages.txt", "w") as file:
        file.write(nltk_chunk_string)

    document = Document(id_=str(page_num), text=page_content)

    sentence_splitter = SentenceSplitter(separator=".", chunk_size=1024, chunk_overlap=128)
    nodes = sentence_splitter.get_nodes_from_documents([document], show_progress=True)
    nodes_chunk_string = "<ch_s>".join((node.get_content() for node in nodes))
    with open(f"./folded_documents/sentence_split_{page_num}pages.txt", "w") as file:
        file.write(nodes_chunk_string)
