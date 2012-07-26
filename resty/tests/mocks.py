class Attrs(object):
    pass


class MockDocument(object):

    def __init__(self, meta={}, content={}, specialized=None):

        self.type = meta.pop('type', 'T')
        self.self = meta.pop('self', 'test://mock_document')

        if 'class' in meta:
            meta['class_'] = meta.pop('class')

        self.meta = Attrs()
        self.content = Attrs()
        self.meta.__dict__.update(meta)
        self.content.__dict__.update(content)

        self._specialized = specialized

    def specialize(self):
        return (
            self._specialized
            or 'specialized %s' % self.self
        )


class MockStateMachine(object):

    def __init__(self):
        self._data = {}

    def load_document(self, URI):
        return self._data[URI]

    def add_document(self, state_id, document):
        self._data[state_id] = document

    def specialize(self, doc):
        return 'specialized %s' % doc.type
