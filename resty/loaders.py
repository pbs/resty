import requests
import json

from documents import DictDocument


class HttpLoader(object):
    def __init__(self, doc_class=DictDocument):
        self._doc_class = doc_class

    def transition_to(self, uri):
         return self._doc_class(json.loads(requests.get(uri)))
