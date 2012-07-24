import json
import unittest2 as unittest


class TestJsonDocument(unittest.TestCase):

    def _get_target(self):
        from resty.documents import JsonDocument
        return JsonDocument

    def _make_one(self, meta={}, content={}):
        meta_copy = dict(('$%s' % key, value) for key, value in meta.items())
        meta_copy.update(content)
        return self._get_target()(json.dumps(meta_copy))

    def test_empty_json(self):
        self.assertRaises(ValueError, self._make_one)

    def test_required_fields(self):
        self.assertRaises(ValueError, self._make_one,
            content={'a': 'a', 'b': 'b'}
        )
        self.assertRaises(ValueError, self._make_one,
            meta={'type': 'type'}
        )
        self.assertRaises(ValueError, self._make_one,
            meta={'self': 'self'}
        )

    def test_minimal_doc(self):
        d = self._make_one(meta={'type': 'type', 'self': 'self'})
        self.assertEqual(d.type, 'type')
        self.assertEqual(d.self, 'self')

    def test_meta_attrs(self):
        d = self._make_shortcut(
            meta={'type': 'type', 'self': 'self', 'a': 'a', 'b': 'b'}
        )
        self.assertEqual(d.meta.a, 'a')
        self.assertEqual(d.meta.b, 'b')

    def test_content_attrs(self):
        d = self._make_shortcut(
            meta={'type': 'type', 'self': 'self'}, content={'a': 'a', 'b': 'b'}
        )
        self.assertEqual(d.content.a, 'a')
        self.assertEqual(d.content.b, 'b')


class DummyStateMachine(object):
    def __init__(self):
        self._data = {}

    def transition_to(self, next_state):
        return self._data[next_state]

    def add_state(self, state_id, state_content):
        self._data[state_id] = state_content


class TestLazyDocument(unittest.TestCase):

    def setup(self):
        self.sm = DummyStateMachine()
        dummy_json_object = json.dumps({
            '$type': 'T',
            '$self': 'test://partial_object',
            'a': 'a', '$b': 'b', 'x': 'x',
        })
        self.sm.add_state('test://partial_object', dummy_json_object)

    def _get_target(self):
        from resty.documents import LazyDocument
        return LazyDocument

    def _make_one(self, meta={}, content={}):
        meta_copy = dict(('$%s' % key, value) for key, value in meta.items())
        meta_copy.update(content)
        return self._get_target()(meta_copy, self.sm)

    def test_no_attrs(self):
        d = self._make_one(meta={'type': 'T', 'self': 'test://partial_object'})
        self.assertEqual(d.content.a, 'a')
        self.assertEqual(d.meta.b, 'b')

    def test_existing_attrs(self):
        d = self._make_one(
            meta={'type': 'T', 'self': 'test://partial_object', 'b': 'bb'},
            content={'a': 'aa'}
        )
        self.assertEqual(d.content.a, 'aa')
        self.assertEqual(d.meta.b, 'bb')
        self.assertEqual(d.content.x, 'x')  # Trigger rerfesh
        self.assertEqual(d.content.a, 'a')
        self.assertEqual(d.meta.b, 'b')

    def test_attr_error(self):
        d = self._make_one(meta={'type': 'T', 'self': 'test://partial_object'})
        self.assertRaises(AttributeError, getattr, d.content, 'not_existing')
        self.assertRaises(AttributeError, getattr, d.meta, 'not_existing')
