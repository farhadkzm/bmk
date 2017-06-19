import hashlib
import json
import subprocess
import sys
import network_selector
import re

class PostmanCollection:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.postman_folders = []

    def add_postman_folder(self, postman_folder):
        self.postman_folders.append(postman_folder)

    def get_collection(self):
        return "{\t\"variables\": [],\n" + \
               "\t\"info\": {\n" + \
               "\t\t\"name\": \"" + self.collection_name + "\",\n" + \
               "\t\t\"_postman_id\": \"" + hashlib.md5(self.collection_name).hexdigest() + "\",\n" + \
               "\t\t\"description\": \"\",\n" + \
               "\t\t\"schema\": \"https://schema.getpostman.com/json/collection/v2.0.0/collection.json\"\n" + \
               "\t},\"item\":[" + ', '.join(
            postman_folder.get_json() for postman_folder in self.postman_folders) + "]}"


# Get recent requests from sandbox
def get_sandbox(sandbox_url, search_term = ''):
    sandbox_name =  re.match( r'.+//(.*)\..+\..*', sandbox_url, re.M|re.I).group(1)
    command_placeholder = "curl -s -X GET -H \"API-Key: api-b3cc25c8-7844-48e5-bc19-5ea37edcea0d\" -H \"Cache-Control: no-cache\"  \"https://getsandbox.com/api/1/activity/search?sourceSandboxes={}&keyword={}\""
    command = command_placeholder.format(sandbox_name, search_term)
    result = subprocess.check_output(command, shell=True)

    return json.loads(result)


def fetch_service_data(mock_url, real_url):
    messages = get_sandbox(mock_url)
    return network_selector.get_postman_folder(messages, real_url)


postman_collection = PostmanCollection('External Services Check')

postman_collection.add_postman_folder(fetch_service_data(sys.argv[1], sys.argv[2]))
# postman_collection.add_postman_folder(fetch_network_selector())

print postman_collection.get_collection()
