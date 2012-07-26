class Client(object):
    def __init__(self, loader):
        self.loader = loader
        self.register_parser = {}
        self.register = {}

    def load_document(self, uri):
        type, text = self.loader(uri)
        doc = self.register_parser[type]
        return doc(self, text)

    def register_document_parser(self, type, class_):
        self.register_parser[type] = class_

    def register_document(self, type, class_):
        self.register[type] = class_

    def specialize(self, class_):
        return self.register[class_.type](class_)

    def load(self, uri):
        d = self.load_document(uri)
        return d.specialize()
