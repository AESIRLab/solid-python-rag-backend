from solid_client_credentials import SolidClientCredentialsAuth, DpopTokenProvider

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import get_response_synthesizer
from llama_index.core import PropertyGraphIndex
from llama_index.core import Document
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import Settings
from llama_index.llms.huggingface import HuggingFaceLLM

import websockets
import ssl
import asyncio
import requests
import json
import time
import dotenv
import os

dotenv.load_dotenv()

SERVER_URI = os.getenv("SERVER_URI")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
UP_ENDPOINT = os.getenv("UP_ENDPOINT")
TOPIC_URI = os.getenv("TOPIC_URI")

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME_LOCAL")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD_LOCAL")
NEO4J_URL = os.getenv("NEO4J_URL_LOCAL")

rag_up_endpoint = os.getenv("RAG_UP_ENDPOINT", "")
DATABASE_NAME = os.getenv("DATABASE_NAME")
UP_CHANGE_ENDPOINT = os.getenv("UP_CHANGE_ENDPOINT")

# rag_up_endpoint = ""

llm = HuggingFaceLLM(model_name="google/gemma-3-1b-it", tokenizer_name="google/gemma-3-1b-it")
Settings.llm = llm

graph_store = Neo4jPropertyGraphStore(
    url=NEO4J_URL,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=DATABASE_NAME
)

index = PropertyGraphIndex.from_existing(property_graph_store=graph_store, 
                                         embed_kg_nodes=False)
retriever = index.as_retriever()

response_sythensizer = get_response_synthesizer(
    response_mode=ResponseMode.COMPACT,
    use_async=True
)

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_sythensizer,
)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def handle_up_endpoint_update(url, auth):
    async with websockets.connect(url, ssl=ssl_context, open_timeout=600, close_timeout=600) as websocket:
        global rag_up_endpoint
        try:
            while True:
                response = await websocket.recv()
                print(response)
                data = json.loads(response)
                # print(data)
                new_uri = data['object']
                data_response = requests.get(new_uri, auth=auth, verify=False)
                json_data = data_response.json()
                new_endpoint = json_data['endpoint']
                rag_up_endpoint = new_endpoint
                print(rag_up_endpoint)
                await asyncio.sleep(0)
        except websockets.exceptions.ConnectionClosed:
            print(f'{url} disconnected')

async def handle_index_update(url, auth):
    async with websockets.connect(url, ssl=ssl_context, open_timeout=600, close_timeout=600) as websocket:
        try:
            while True:
                response = await websocket.recv()
                print(response)
                data = json.loads(response)
                # print(data)
                new_uri = data['object']
                data_response = requests.get(new_uri, auth=auth, verify=False)
                print(data_response.headers['content-type'])
                content_type = data_response.headers['content-type']
                if content_type == 'application/json':
                    json_data = data_response.json()
                    data = json_data['content']
                elif content_type == 'text/turtle':
                    pass
                    # handle rdf
                    # data =
                else:
                    data = data_response.content 
                # insert new index with data as Document
                index.insert(Document(data))
                await asyncio.sleep(0)
        except websockets.exceptions.ConnectionClosed:
            print(f'{url} disconnected')


async def handle_connection(url, auth):
    # print("started!")
    async with websockets.connect(url, ssl=ssl_context, open_timeout=600, close_timeout=600) as websocket:
        try:
            while True:
                response = await websocket.recv()
                # print(response)
                data = json.loads(response)
                # print(data)
                new_uri = data['object']
                data_response = requests.get(new_uri, auth=auth, verify=False)
                json_data = data_response.json()
                print(json_data)
                # start = time.time()
                llm_response = await query_engine.aquery(json_data['query'])
                print(str(llm_response))
                # print(f"query executed in {time.time() - start} seconds")
                print(f"sending query to {rag_up_endpoint}")
                response = requests.put(rag_up_endpoint, headers={'Content-Type': 'application/json'}, 
                                        json={
                                            'generated_text': str(llm_response), 
                                            'query_id': json_data['query_id'], 
                                        }
                                        )
                print(response)
                await asyncio.sleep(0)
        except websockets.exceptions.ConnectionClosed:
            print(f'{url} disconnected')

async def main():
    response = requests.post(
        SERVER_URI + 'idp/credentials/', 
        headers={'content-type': 'application/json'}, 
        json={'email': EMAIL, 'password': PASSWORD, 'name': 'my-token'},
        verify=False)
    json_data = response.json()
    id = json_data['id']
    secret = json_data['secret']
    token_provider = DpopTokenProvider(
        issuer_url=SERVER_URI,
        client_id=id,
        client_secret=secret
    )
    auth = SolidClientCredentialsAuth(token_provider)

    response = requests.get(UP_CHANGE_ENDPOINT,auth=auth,verify=False)
    if response.status_code not in range(200,300):
        response = requests.put(UP_CHANGE_ENDPOINT, auth=auth, verify=False)
        if response.status_code in range(200, 300):
            print(f"successfully created UP CHANGE ENDPOINT at {UP_CHANGE_ENDPOINT}")
        else:
            print(f"failed to create UP CHANGE ENDPOINT at {UP_CHANGE_ENDPOINT} with response: {response}")
            exit(-1)

    topics = [
        TOPIC_URI,
        UP_CHANGE_ENDPOINT,
        "https://ec2-18-119-19-244.us-east-2.compute.amazonaws.com/dorothy/profile/wikipedia_pages/",
        "https://ec2-18-119-19-244.us-east-2.compute.amazonaws.com/zeke/profile/wikipedia_pages/",
        # "https://ec2-18-119-19-244.us-east-2.compute.amazonaws.com/kaylee/profile/wikipedia_pages/"
    ]
    # topic = TOPIC_URI
    
    listen_uris = []
    for topic in topics:
        ws_response = requests.post(
            SERVER_URI + '.notifications/WebSocketChannel2023/', 
            headers={'content-type': 'application/ld+json'}, 
            json={"@context": ["https://www.w3.org/ns/solid/notification/v1"],
    "type": "http://www.w3.org/ns/solid/notifications#WebSocketChannel2023", "topic": topic}, 
            verify=False,
            auth=auth)
        ws_data = ws_response.json()
        listen_uri = ws_data['receiveFrom']
        listen_uris.append(listen_uri)
    print(listen_uris)

    things = [
        (listen_uris[0], auth, handle_connection),
        (listen_uris[1], auth, handle_up_endpoint_update),
    ]
    for uri in listen_uris[2:]:
        things.append((uri, auth, handle_index_update))

    tasks = [f(uri, auth) for uri, auth, f in things]
    print(tasks)
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())