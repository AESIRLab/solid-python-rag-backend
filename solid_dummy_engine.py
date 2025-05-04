from solid_client_credentials import SolidClientCredentialsAuth, DpopTokenProvider

import websockets
import ssl
import asyncio
import requests
import json
import time
import dotenv
import os

import warnings
warnings.filterwarnings("ignore")
dotenv.load_dotenv()

SERVER_URI = os.getenv("SERVER_URI")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
RAG_UP_ENDPOINT = os.getenv("RAG_UP_ENDPOINT")
TOPIC_URI = os.getenv("TOPIC_URI")
print(RAG_UP_ENDPOINT)

async def handle_connection(websocket, auth):
    print("started!")
    response = await websocket.recv()
    pod_received_time = time.time_ns() // 1000000
    data = json.loads(response)
    print(data)
    new_uri = data['object']
    data_response = requests.get(new_uri, auth=auth, verify=False)
    json_data = data_response.json()
    print(json_data)
    # llm_response = await query_engine.aquery(json_data['query'])
    
    response = requests.put(RAG_UP_ENDPOINT, headers={'Content-Type': 'application/json'}, 
                            json={'generated_text': json_data['query'], 
                                  'query_id': json_data['query_id'],
                                  'pod_received_time': pod_received_time,
                                  'app_sent_time': json_data['app_sent_time'],
                                  'up_sent_time': time.time_ns() // 1000000 })
    print(pod_received_time)

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