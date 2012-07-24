import requests
import json

from documents import JsonDocument


class HttpLoader(object):
    def __init__(self, doc_class=JsonDocument):
        self._doc_class = doc_class

    def transition_to(self, uri):
         return self._doc_class(json.dumps(requests.get(uri)))
