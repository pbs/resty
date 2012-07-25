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

    def transition_to(self, next_state):
        return self._data[next_state]

    def add_state(self, state_id, state_content):
        self._data[state_id] = state_content
