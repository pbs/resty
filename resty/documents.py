import copy
import json


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
                if class_ is None or class_ == item.get('$class'):
                    result.append(item)

        if len(result) == 1:
            return self._sm.load_document(result.pop()['$self'])

        raise ValueError

    def service(self, name):
        data = self.meta.services.get(name)
        if not data:
            raise ValueError
        return self._sm.load_data(data['$self'])

    def items(self):
        for item in self.meta.items:
            yield self._sm.load_data(item['$self'])

    def specialize(self):
        return self._sm.specialize(self)

    def page(self, page):
        page_uri = self.meta.page_control.replace('{page}', str(page))
        return self._sm.load_document(page_uri)
