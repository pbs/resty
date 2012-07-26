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
        filter_uri = self.meta.filters[name]
        for key, value in kwargs.iteritems():
            filter_uri = filter_uri.replace('{' + key + '}', value)
        return self._sm.load_document(filter_uri)

    def related(self, relation, klass=None):
        related = copy.deepcopy(self.meta.links)

        result = []
        for item in related:
            if relation == item.get('$relationship'):
                item.pop('$relationship')
                if klass is None or klass == item.get('$class'):
                    result.append(item)

        if len(result) == 1:
            return JsonDocument(self._sm, json.dumps(result.pop()))

        raise ValueError

    def get_service_data(self, name):
        data = self.meta.services.get(name)
        if not data:
            raise ValueError
        return data

    def get_items(self):
        for item in self.meta.items:
            yield item


class Resource(JsonDocument):
    def __init__(self, data):
        super(Resource, self).__init__(data)


class Collection(JsonDocument):
    def __init__(self, data):
        super(Collection, self).__init__(data)


class Service(JsonDocument):
    def __init__(self, data):
        super(Service, self).__init__(data)
