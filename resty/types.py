class Resource(object):
    def __init__(self, doc):
        self.self = doc.self
        self.class_ = doc.meta.class_
        if hasattr(doc.meta, 'hash'):
            self.hash = doc.meta.hash
        if hasattr(doc.meta, 'id'):
            self.id = doc.meta.id
        if hasattr(doc.meta, 'created'):
            self.created = doc.meta.created
        if hasattr(doc.meta, 'edited'):
            self.edited = doc.meta.edited


class Collection(object):
    def __init__(self, doc):
        self.doc = doc


class Service(object):
    def __init__(self, doc):
        self.doc = doc
