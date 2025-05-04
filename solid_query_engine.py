from solid_client_credentials import SolidClientCredentialsAuth, DpopTokenProvider

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import get_response_synthesizer
from llama_index.core import PropertyGraphIndex
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

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URL = os.getenv("NEO4J_URL")

llm = HuggingFaceLLM(model_name="google/gemma-3-1b-it", tokenizer_name="google/gemma-3-1b-it")
Settings.llm = llm

graph_store = Neo4jPropertyGraphStore(
    url=NEO4J_URL,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database="sixpagesgemma"
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

async def handle_connection(websocket, auth):
    print("started!")
    response = await websocket.recv()
    # print(response)
    data = json.loads(response)
    # print(data)
    new_uri = data['object']
    data_response = requests.get(new_uri, auth=auth, verify=False)
    json_data = data_response.json()
    print(json_data)
    start = time.time()
    llm_response = await query_engine.aquery(json_data['query'])
    print(str(llm_response))
    print(f"query executed in {time.time() - start} seconds")

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
    
    topic = TOPIC_URI
    
    ws_response = requests.post(
        SERVER_URI + '.notifications/WebSocketChannel2023/', 
        headers={'content-type': 'application/ld+json'}, 
        json={"@context": ["https://www.w3.org/ns/solid/notification/v1"],
  "type": "http://www.w3.org/ns/solid/notifications#WebSocketChannel2023", "topic": topic}, 
        verify=False,
        auth=auth)
    ws_data = ws_response.json()
    listen_uri = ws_data['receiveFrom']
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async for websocket in websockets.connect(listen_uri, ssl=ssl_context, open_timeout=600, close_timeout=600):
        await handle_connection(websocket, auth)

if __name__ == '__main__':
    asyncio.run(main())