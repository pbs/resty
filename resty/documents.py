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
        if not hasattr(self.meta, 'filters'):
            raise DocumentError('No filters field.')
        if name not in self.meta.filters:
            raise ValueError

        filter_uri = self.meta.filters[name]
        for key, value in kwargs.iteritems():
            filter_uri = filter_uri.replace('{' + key + '}', value)
        return self._sm.load_document(filter_uri)

    def related(self, relation, class_=None):
        if not hasattr(self.meta, 'links'):
            raise DocumentError('No links field.')
        related = copy.deepcopy(self.meta.links)

        result = []
        for item in related:
            if relation == item.get('$relationship'):
                item.pop('$relationship')
                if class_ in [None, item.get('$class'), item.get('$elements')]:
                    result.append(item)

        if len(result) == 1:
            return self._from_subdoc(result.pop())

        raise ValueError

    def service(self, name):
        if not hasattr(self.meta, 'services'):
            raise DocumentError('No services field.')
        data = self.meta.services.get(name)
        if not data:
            raise ValueError
        return self._from_subdoc(data)

    def items(self):
        if not hasattr(self.meta, 'items'):
            raise DocumentError('No items field.')
        result = []
        for item in self.meta.items:
            result.append(self._from_subdoc(item))
        return result

    def specialize(self):
        return self._sm.specialize(self)

    def page(self, page):
        if not hasattr(self.meta, 'page_control'):
            raise DocumentError('No page_control field.')
        page_uri = self.meta.page_control.replace('{page_num}', str(page))
        return self._sm.load_document(page_uri)

    def _from_subdoc(self, subdoc):
        return self._sm.load_document(subdoc['$self'])


class LazyProperties(object):
    def __init__(self, loader):
        self._arg_loader = loader

    def __getattr__(self, name):
        return self._arg_loader(name)


class LazyDocument(object):
    def __init__(self, state_machine, doc):
        self._sm = state_machine

        self._original_doc = doc
        self._loaded_doc = None
        self._loaded = False

        self.type = doc.type
        self.self = doc.self

        self.meta = LazyProperties(self._get_meta)
        self.content = LazyProperties(self._get_content)

    def _get_meta(self, attr_name):
        if self._loaded:
            return getattr(self._loaded_doc.meta, attr_name)
        try:
            return getattr(self._original_doc.meta, attr_name)
        except AttributeError:
            self._loaded = True
            url = self._original_doc.self
            self._loaded_doc = self._sm.load_document(url)
            return self._get_meta(attr_name)

    def _get_content(self, attr_name):
        if self._loaded:
            return getattr(self._loaded_doc.content, attr_name)
        try:
            return getattr(self._original_doc.content, attr_name)
        except AttributeError:
            self._loaded = True
            url = self._original_doc.self
            self._loaded_doc = self._sm.load_document(url)
            return self._get_content(attr_name)

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
        if self._loaded:
            return getattr(self._loaded_doc, method_name)(*args, **kwargs)
        try:
            return getattr(self._original_doc, method_name)(*args, **kwargs)
        except DocumentError:
            self._loaded = True
            self._loaded_doc = self._sm.load_document(self._original_doc.self)
            return self._defer_method(method_name, *args, **kwargs)


class LazyJsonDocument(JsonDocument):
    def _from_subdoc(self, subdoc):
        return LazyDocument(
            self._sm, LazyJsonDocument(
                self._sm, json.dumps(subdoc)
            )
        )
