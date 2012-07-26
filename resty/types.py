class Resource(object):
    def __init__(self, doc):
        self.doc = doc
        self.self = doc.self
        self.class_ = doc.meta.class_

    @property
    def edited(self):
        return self.doc.meta.edited

    @property
    def created(self):
        return self.doc.meta.created

    @property
    def hash(self):
        return self.doc.meta.hash

    @property
    def id(self):
        return self.doc.meta.id


class Collection(object):
    def __init__(self, doc):
        self.doc = doc


class Service(object):
    def __init__(self, doc):
        self.doc = doc
