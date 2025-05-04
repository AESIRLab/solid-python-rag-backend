### Solid Rag backend service ###


## .env variables ##
The required fields in the .env file are listed below:

NEO4J_USERNAME - This is the username you should use to authenticate with your Neo4J database.
NEO4J_PASSWORD - This is the password you should use to authenticate with your Neo4J database.
NEO4J_URL - This is the url served to access the Neo4J api for your database.
SERVER_URI - This is the uri of the Solid server where your pod is hosted.
EMAIL - This is the email you use to access your WebID.
PASSWORD - This is the password used to access your WebID and Solid Pod.
RAG_UP_ENDPOINT - This is the UnifiedPush endpoint which the Solid Rag Service app will receive from.
TOPIC_URI - This is the URI of the resource which you will listen to for remote query files to be sent.
TESTING_TOPIC_URI - For testing purposes with the dummy engine and post dummmy file.

## chunkify_wikipedia ##
This folder contains the code used to create chunks and the corresponding data files which were fed
to the Android application for embedding.

## solid_resource_handlers ##
update_acl - This is code used to update remote ACLs to accept a WebID for writing into a different agent's resource.
solid_post_dummy - used to test websocket listening and query JSON formatting.
solid_store_wikipedia_pages - code used to load wikipedia pages into same Pod or a different user's pod.

## knowledge_graph_builders ##
Code used with Gemma3:1B to construct knowledge graphs from wikipedia pages.

## evaluations ##
experiment_judge - code which used Qwen3:14B in thinking mode to evaluate responses.

## / ##
solid_query_engine - version which uses environment variable and user information to load Neo4j database and establish a connection to a Pod and topic and send responses to the ntfy server using UnifiedPush protocol.
solid_dummy_engine - dummy version which sends messages, does no inference, used for determining round-trip-times from unifiedpush server, solid server, and Android RAG service application.