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

    def _make_shortcut(self, meta={}, content={}):
        minimal_dict = {'type': 'type', 'self': 'self'}
        minimal_dict.update(meta)
        return self._make_one(minimal_dict, content)

    def test_empty_json(self):
        self.assertRaises(ValueError, self._make_one, {})

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
        d = self._make_shortcut()
        self.assertEqual(d.type, 'type')
        self.assertEqual(d.self, 'self')

    def test_meta_attrs(self):
        d = self._make_shortcut(meta={'a': 'a', 'b': 'b'})
        self.assertTrue(hasattr(d.meta, 'a'))
        self.assertEqual(d.meta.a, 'a')
        self.assertTrue(hasattr(d.meta, 'b'))
        self.assertEqual(d.meta.b, 'b')

    def test_user_attrs(self):
        d = self._make_shortcut(content={'a': 'a', 'b': 'b'})
        self.assertTrue(hasattr(d.user, 'a'))
        self.assertEqual(d.user.a, 'a')
        self.assertTrue(hasattr(d.user, 'b'))
        self.assertEqual(d.user.b, 'b')


class TestDictDocument(TestJsonDocument):
    def _get_target(self):
        from resty.documents import DictDocument
        return DictDocument

    def _make_one(self, meta={}, content={}):
        meta_copy = dict(('$%s' % key, value) for key, value in meta.items())
        meta_copy.update(content)
        return self._get_target()(meta_copy)
