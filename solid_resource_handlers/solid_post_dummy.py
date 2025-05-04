import asyncio
import requests
from solid_client_credentials import SolidClientCredentialsAuth, DpopTokenProvider
import ssl
import warnings
import dotenv
import os

dotenv.load_dotenv()

# Ignore all warnings
warnings.filterwarnings("ignore")
SERVER_URI = os.getenv("SERVER_URI")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
UP_ENDPOINT = os.getenv("UP_ENDPOINT")
TESTING_TOPIC_URI = os.getenv("TESTING_TOPIC_URI")

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
    
    topic = TESTING_TOPIC_URI # 'https://ec2-18-119-19-244.us-east-2.compute.amazonaws.com/dorothy/profile/'
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

#     response = requests.post(
#         topic,
#         headers={'content-type': 'application/json'}, 
#         json={"query_id": 2,
#   "query": "Please explain the important people in Darwin's life and his contributions to society", }, 
#         verify=False,
#         auth=auth)
    print(topic)
    response = requests.put(
        topic + 'test.json',
        headers={'content-type': 'application/json'}, 
        json={"query_id": 2,
  "query": "Please explain the important people in Darwin's life and his contributions to society", }, 
        verify=False,
        auth=auth)

    # response = requests.get(
    #     topic,
    #     verify=False,
    #     auth=auth)
    print(response.text)
    print(response.status_code)
    

if __name__ == '__main__':
    asyncio.run(main())