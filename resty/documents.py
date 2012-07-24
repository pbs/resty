import json


class JsonDocument(object):
    def __init__(self, data):
        self._data = json.loads(data)
        self._is_valid()

        self.type = self._data['$type']
        self.self = self._data['$self']
        self.meta = dotdictify(self._data)
        self.content = dotdictify(self._data)

    def _is_valid(self):
        if not self._data:
            raise ValueError

        required = ['$type', '$self']
        for r in required:
            if r not in self._data:
                raise ValueError


class Resource(JsonDocument):
    def __init__(self, data):
        super(Resource, self).__init__(data)


class Collection(JsonDocument):
    def __init__(self, data):
        super(Collection, self).__init__(data)


class Service(JsonDocument):
    def __init__(self, data):
        super(Service, self).__init__(data)


class dotdictify(dict):
    marker = object()
    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError, 'expected dict'

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, dotdictify):
            value = dotdictify(value)
        key = key.replace('$', '')
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        found = self.get(key, dotdictify.marker)
        if found is dotdictify.marker:
            found = dotdictify()
            dict.__setitem__(self, key, found)
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__
