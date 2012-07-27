import copy
import json


class DocumentError(RuntimeError):
    pass


class Properties(object):
    def __init__(self, data, prefix=''):
        self.data = data
        self.prefix = prefix

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if name == 'class_':
                prefixed = self.prefix + name[:-1]
            else:
                prefixed = self.prefix + name

            if prefixed in self.data:
                object.__setattr__(self, name, self.data[prefixed])
            return object.__getattribute__(self, name)


class JsonDocument(object):
    def __init__(self, state_machine, data):
        data = json.loads(data)
        self._sm = state_machine
        self._data = self._validated(data)

        self.type = self._data.pop('$type')
        self.self = self._data.pop('$self')

        self.meta = Properties(self._data, prefix='$')
        self.content = Properties(self._data)

    def _validated(self, data):
        if not data:
            raise ValueError

        required = ['$type', '$self']
        for r in required:
            if r not in data:
                raise ValueError
        return data

    def filter(self, name, **kwargs):
        if name not in self.meta.filters:
            raise ValueError

        filter_uri = self.meta.filters[name]
        for key, value in kwargs.iteritems():
            filter_uri = filter_uri.replace('{' + key + '}', value)
        return self._sm.load_document(filter_uri)

    def related(self, relation, class_=None):
        related = copy.deepcopy(self.meta.links)

        result = []
        for item in related:
            if relation == item.get('$relationship'):
                item.pop('$relationship')
                if class_ in [None, item.get('$class'), item.get('$elements')]:
                    result.append(item)

        if len(result) == 1:
            return self._sm.load_document(result.pop()['$self'])

        raise ValueError

    def service(self, name):
        data = self.meta.services.get(name)
        if not data:
            raise ValueError
        return self._sm.load_document(data['$self'])

    def items(self):
        for item in self.meta.items:
            yield self._sm.load_document(item['$self'])

    def specialize(self):
        return self._sm.specialize(self)

    def page(self, page):
        page_uri = self.meta.page_control.replace('{page_num}', str(page))
        return self._sm.load_document(page_uri)


class LazyProperties(object):
    def __init__(self, data, prefix=''):
        self.data = data
        self.prefix = prefix

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if name == 'class_':
                prefixed = self.prefix + name[:-1]
            else:
                prefixed = self.prefix + name

            if prefixed in self.data:
                object.__setattr__(self, name, self.data[prefixed])
            return object.__getattribute__(self, name)


class LazyDocument(object):
    def __init__(self, state_machine, doc):
        self._sm = state_machine

        self.original_doc = doc
        self.loaded_doc = None
        self.loaded = False

        self.type = doc.type
        self.self = doc.self

    #def __getattribute__(self, name):
        #try:
            #return object.__getattribute__(self, name)
        #except AttributeError:
            #if self.loaded is False:
                #self.loaded = True
                #self.loaded_doc = self._sm.load_document(self.self)
                #object.__setattr__(self, 'meta', self.loaded_doc.meta)
                #object.__setattr__(self, 'content', self.loaded_doc.content)

            #return object.__getattribute__(self, name)

    @property
    def meta(self):
        return self.original_doc.meta

    @property
    def content(self):
        return self.original_doc.content

    def filter(self, name, **kwargs):
        return self._defer_method('filter', name, **kwargs)

    def related(self, relation, class_=None):
        return self._defer_method('related', relation, class_=class_)

    def service(self, name):
        return self._defer_method('service', name)

    def items(self):
        return self._defer_method('items')

    def specialize(self):
        return self._sm.specialize(self)

    def page(self, page):
        return self._defer_method('page', page)

    def _defer_method(self, method_name, *args, **kwargs):
        if self.loaded:
            return getattr(self.loaded_doc, method_name)(*args, **kwargs)
        try:
            return getattr(self.original_doc, method_name)(*args, **kwargs)
        except DocumentError:
            self.loaded = True
            self.loaded_doc = self._sm.load_document(self.original_doc.self)
            return self._defer_method(method_name, *args, **kwargs)
