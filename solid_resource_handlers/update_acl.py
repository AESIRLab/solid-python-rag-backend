from rdflib import URIRef, BNode, Namespace, Literal, RDF, Graph
import requests
from uuid import uuid4
import json
from solid_client_credentials import DpopTokenProvider, SolidClientCredentialsAuth
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

ACL = Namespace("http://www.w3.org/ns/auth/acl#")

def parse_link_headers(link_headers) -> dict:
    rels_dict = {}
    for val in link_headers.values():
        pairings = val.split(",")
        for pair in pairings:
            link, rel = pair.split(";")
            trimmed_link = link.replace("<", "").replace(">", "")
            rel = rel.split("=")[1].replace("\"", "")
            rels_dict[rel] = trimmed_link
    return rels_dict

def get_link_headers(response) -> dict:
    link_headers = {header: response.headers[header] for header in response.headers.keys() if header == 'Link'}
    return link_headers

def links_has_acl(links_dict: dict) -> bool:
    return 'acl' in links_dict.keys()

def get_acl_resource(links_dict: dict) -> str:
    if links_has_acl(links_dict):
        acl_uri = links_dict['acl']
        return acl_uri
    
def add_web_id_to_acl_resource(own_webid: str, acl_text: str, web_id: str, resource: str, modes: list = ["Read"]) -> Graph:
    '''
    modes = "Read" | "Write" | "Append"
    '''
    print(f"resource split: {resource.split('#')[0]}")
    base_uri = resource.split('#')[0]
    graph = Graph(base=base_uri)
    graph.parse(data=acl_text, format='text/turtle', publicID=base_uri)
    # print(f"parsed graph: {graph.serialize()}")
    graph.bind("acl", ACL)
    graph.add((URIRef(base_uri + "#owner"), RDF.type, ACL.Authorization))
    graph.add((URIRef(base_uri + "#owner"), ACL.accessTo, URIRef(resource)))
    graph.add((URIRef(base_uri + "#owner"), ACL.agent, URIRef(own_webid)))
    graph.add((URIRef(base_uri + "#owner"), ACL.mode, ACL.Read))        
    graph.add((URIRef(base_uri + "#owner"), ACL.mode, ACL.Write))        
    # graph.add((URIRef(base_uri + "#owner"), ACL.mode, ACL.Append))
    graph.add((URIRef(base_uri + "#owner"), ACL.mode, ACL.Control))
    graph.add((URIRef(base_uri + "#owner"), ACL.default, URIRef(resource)))
    
    fragment = f"#{str(uuid4())}"
    identifier = base_uri + fragment
    graph.add((URIRef(identifier), RDF.type, ACL.Authorization))
    graph.add((URIRef(identifier), ACL.accessTo, URIRef(resource)))
    graph.add((URIRef(identifier), ACL.agent, URIRef(web_id)))
    
    for mode in modes:
        if mode == "Read":
            graph.add((URIRef(identifier), ACL.mode, ACL.Read))        
        elif mode == "Write":
            graph.add((URIRef(identifier), ACL.mode, ACL.Write))        
        elif mode == "Append":
            graph.add((URIRef(identifier), ACL.mode, ACL.Append))
        else:
            pass
    return graph


def main():
    PERMS_WEBID = 'https://ec2-18-119-19-244.us-east-2.compute.amazonaws.com/zach/profile/card#me'
    with open('credentials_map.json', 'r') as file:
        data = json.load(file)
    user_list = data['users']
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

        BASE_URI = "".join(user['web_id'].rsplit('/', 1)[0:-1]) + '/'
        TARGET_URI = BASE_URI + 'wikipedia_pages/'
        response = requests.get(TARGET_URI, auth=auth, verify=False)
        
        print(f" response code {response.status_code} for uri {TARGET_URI}")
        if response.status_code not in range(200, 300):
            response = requests.put(TARGET_URI, auth=auth, verify=False)
        # # 2. Now start the ACL handling
        # # 3. get all the Link headers from the response
        link_headers = get_link_headers(response)
        print(f"link_headers: {link_headers}")
        # # 4. the link headers must be parsed into a dict
        parsed_link_headers = parse_link_headers(link_headers)
        print(f"parsed headers: {parsed_link_headers}")
        # # 5. extract the one that has the kind rel="acl"
        # # that will be your access control list for the resource from 1.
        acl_resource_uri = get_acl_resource(parsed_link_headers)
        if acl_resource_uri == None:
            acl_resource_uri = TARGET_URI + ".acl"
        # # 6. get the actual ACL file contents
        response = requests.get(acl_resource_uri, auth=auth, verify=False)
        print(f"acl response: {response}")
        if response.status_code not in range(200, 300):
            # # 7. feed the text of the ACL document, the WebID you want to add, the resource URI, and the modes as a 
            # # list. default for modes is READ so it can be left empty
            g = add_web_id_to_acl_resource(user['web_id'], '', PERMS_WEBID, TARGET_URI, ["Read", "Append"])
            headers = {
                'content-type': 'text/turtle'
            }
            data = g.serialize()
            print(data)
            # # 8. serialize the graph, set the header, pass in the auth to PUT
            # # for the acl resource uri since we are changing the file in its entirety
            # # could possibly be PATCH but this is safer(?)
            response = requests.put(
                acl_resource_uri, 
                headers=headers, 
                auth=auth, 
                verify=False, 
                data=data)
            print(response)
        print(f"acl response code: {response.status_code}")
        response = requests.get(acl_resource_uri, verify=False, auth=auth)
        print(f"new acl text: {response.text}")


if __name__ == '__main__':
    main()