import json


class PostmanFolder(object):
    def __init__(self):
        self.description = ''
        pass

    def get_json(self):
        # return json.dumps({
        #     "name": postman_folder.name,
        #     "description": "",
        #     "item": [postman_folder.get_postman_requests()]
        # })
        #
        return json.dumps(self.__dict__)
