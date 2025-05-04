import json
from solid_client_credentials import DpopTokenProvider, SolidClientCredentialsAuth
import requests
import wikipedia
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

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

def main():
    with open('credentials_map.json', 'r') as file:
        data = json.load(file)
    user_list = data['users']
    i = 0
    for user in user_list:
        # print(user)
        ############## stuff for CSS auth ###################
        data = {
            'email' : user['email'],
            'password' : user['password'],
            'name': 'my-random-token'
        }
        response = requests.post(
            user['server_uri']+'idp/credentials/', 
            headers={'Content-Type': 'application/json'}, 
            data=json.dumps(data),
            verify=False)
        json_data = response.json()
        client_id, client_secret = json_data['id'], json_data['secret']
        #####################################################
        token_provider = DpopTokenProvider(
            issuer_url=user['server_uri'],
            client_id=client_id,
            client_secret=client_secret
        )

        auth = SolidClientCredentialsAuth(token_provider)
        wiki_page_one = wikipedia.page(wikipedia_pages[i])
        wiki_page_two = wikipedia.page(wikipedia_pages[i+1]) 
        TARGET_URI = "".join(user['web_id'].rsplit('/', 1)[0:-1]) + '/wiki_data/'
        print(TARGET_URI + wikipedia_pages[i])
        print(TARGET_URI + wikipedia_pages[i+1])
        response = requests.put(
            TARGET_URI + wikipedia_pages[i] + ".json",
            headers={'content-type': 'application/json'}, 
            json={"page_id": wiki_page_one.pageid,
    "page_content": wiki_page_one.content, }, 
            verify=False,
            auth=auth)
        print(f"first response: {response.status_code}")
        response = requests.put(
            TARGET_URI + wikipedia_pages[i+1],
            headers={'content-type': 'application/json'}, 
            json={"page_id": wiki_page_two.pageid,
    "page_content": wiki_page_two.content, }, 
            verify=False,
            auth=auth)
        print(f"second response: {response.status_code}")
        i += 2
        # response = requests.get(TARGET_URI, auth=auth, verify=False)
        # print(f" response code {response.status_code} for uri {TARGET_URI}")
        


if __name__ == '__main__':
    main()