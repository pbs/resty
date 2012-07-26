from resty.documents import JsonDocument


class Resource(JsonDocument):
    def __init__(self, data):
        super(Resource, self).__init__(data)


class Collection(JsonDocument):
    def __init__(self, data):
        super(Collection, self).__init__(data)


class Service(JsonDocument):
    def __init__(self, data):
        super(Service, self).__init__(data)
