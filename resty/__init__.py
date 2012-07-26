import requests

class Client(object):
    def __init__(self, loader):
        self.loader = loader
        self.register_parser = {}
        self.register = {}

    def load_document(self, uri):
        type_, text = self.loader(uri)
        doc = self.register_parser[type_]
        return doc(self, text)

    def register_document_parser(self, type_, class_):
        self.register_parser[type_] = class_

    def register_document(self, type_, class_):
        self.register[type_] = class_

    def specialize(self, class_):
        return self.register[class_.type](class_)

    def load(self, uri):
        d = self.load_document(uri)
        return d.specialize()


def http_loader(uri):
    response = requests.get(uri)
    return response.headers.get('content-type'), response.text
