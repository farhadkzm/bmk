from  postman_folder import PostmanFolder


def filter_duplicates(messages):
    captured_requests = []
    for message in messages:
        if not basic_duplicate_request_finder(message["messageObject"]["request"], captured_requests):
            captured_requests.append(message["messageObject"]["request"])
    return captured_requests


def get_postman_folder(messages, real_url):
    folder = PostmanFolder()

    captured_requests = filter_duplicates(messages)
    # print "Filtering {} items to {}".format(len(messages), len(captured_requests))

    folder.name = get_folder_name(messages[0])

    folder.item = []
    index = 0
    for request in captured_requests:
        index += 1
        folder.item.append(create_mock_request(request, index))
        folder.item.append(create_real_request(request, index, real_url))

    return folder


def create_mock_test_script():
    test_script = '''

postman.clearGlobalVariable("mock_response");
postman.setGlobalVariable("mock_response", responseBody);

    '''

    return test_script.splitlines()


def create_real_test_script():
    test_script = '''


mock_response = postman.getGlobalVariable("mock_response");

mock_response = mock_response.replace(/\\s+|\\t+|\\r+|\\n+/gm, '').trim();
real_response = responseBody.replace(/\\s+|\\t+|\\r+|\\n+/gm, '').trim();

tests["Body matches string"] = mock_response === real_response;


    '''

    return test_script.splitlines()


def create_mock_request(request, index):
    request_object = {
        "name": "{}-{}-MOCK".format(request["sandboxName"], index),
        "event": [
            {
                "listen": "test",
                "script": {
                    "type": "text/javascript",
                    "exec": create_mock_test_script()
                }
            }
        ],
        "request": {

            "url": "https://{}.getsandbox.com{}".format(request['fullSandboxName'], request['rawUrl']),
            "method": request['method'],
            "header": [{'key': key, 'value': value} for key, value in request['headers'].iteritems()],

            "body": {
                "mode": "raw",
                "raw": request['body']
            },
            "description": ""
        },
        "response": []
    }
    return request_object


def create_real_request(request, index, real_url):

    request_object = {
        "name": "{}-{}-REAL".format(request["sandboxName"], index),
        "event": [
            {
                "listen": "test",
                "script": {
                    "type": "text/javascript",
                    "exec": create_real_test_script()
                }
            }
        ],
        "request": {

            "url": real_url,
            "method": request['method'],
            "header": [{'key': key, 'value': value} for key, value in request['headers'].iteritems()],

            "body": {
                "mode": "raw",
                "raw": request['body']
            },
            "description": ""
        },
        "response": []
    }
    return request_object


def basic_duplicate_request_finder(request, captured_requests):
    method = request['method']
    url = request['url']
    sandbox = request['sandboxName']
    body = request['body']
    for _req in captured_requests:
        if method == _req['method'] and url == _req['url'] and sandbox == _req['sandboxName'] and body == _req['body']:
            return True
    return False


def get_folder_name(message):
    return message["messageObject"]["sandboxName"]
