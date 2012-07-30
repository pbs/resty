import math


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

    @property
    def content(self):
        return self.doc.content

    def related(self, relation, class_=None):
        rel = self.doc.related(relation, class_)
        return rel.specialize()


class Collection(object):
    def __init__(self, doc):
        self.doc = doc
        self.self = doc.self

    @property
    def hash(self):
        return self.doc.meta.hash

    @property
    def elements(self):
        return self.doc.meta.elements

    def filter(self, name, **kwargs):
        filtered = self.doc.filter(name, **kwargs)
        return filtered.specialize()

    def items(self):
        result = []
        if not hasattr(self.doc.meta, 'page'):
            for item in self.doc.items():
                result.append(item.specialize())
        else:
            total_nr_pages = math.ceil(
                float(self.doc.meta.items_count)
                / float(self.doc.meta.page_size)
            )
            for page_nr in range(1, int(total_nr_pages) + 1):
                page = self.doc.page(page_nr)
                for item in page.items():
                    result.append(item.specialize())
        return result


class Service(object):
    def __init__(self, doc):
        self.doc = doc
        self.self = doc.self

    @property
    def hash(self):
        return self.doc.meta.hash

    @property
    def content(self):
        return self.doc.content

    def service(self, name):
        service = self.doc.service(name)
        return service.specialize()
