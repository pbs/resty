class MockDocument(object):

    def __init__(self, meta={}, content={}):

        self.type = meta.pop('type', 'T')
        self.self = meta.pop('self', 'test://mock_document')

        self.meta = object()
        self.content = object()
        self.meta.__dict__.update(meta)
        self.content.__dict__.update(content)


class MockStateMachine(object):

    def __init__(self):
        self._data = {}

    def load_document(self, URI):
        return self._data[URI]

    def add_document(self, state_id, document):
        self._data[state_id] = document
