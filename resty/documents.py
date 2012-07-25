class Properties(object):
    def __init__(self, data, prefix=''):
        self.data = data
        self.prefix = prefix

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if self.prefix+name in self.data:
                object.__setattr__(self, name, self.data[self.prefix+name])
            return object.__getattribute__(self, name)


class DictDocument(object):
    def __init__(self, data):
        self._data = self._validated(data)

        self.type = self._data['$type']
        self.self = self._data['$self']

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

    def get_filter_uri(self, name, **kwargs):
        filter_uri = self._data['$filters'][name]
        for key, value in kwargs.iteritems():
            filter_uri = filter_uri.replace('{' + key + '}', value)
        return filter_uri


class Resource(DictDocument):
    def __init__(self, data):
        super(Resource, self).__init__(data)


class Collection(DictDocument):
    def __init__(self, data):
        super(Collection, self).__init__(data)


class Service(DictDocument):
    def __init__(self, data):
        super(Service, self).__init__(data)
