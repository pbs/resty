import unittest2 as unittest

from resty.tests.mocks import MockDocument


class TestResource(unittest.TestCase):

    def _get_target(self):
        from resty.types import Resource
        return Resource

    def _make_one(self, doc):
        return self._get_target()(doc)

    def test_known_meta(self):
        r = self._make_one(
            MockDocument(meta={
                'hash': 'hash',
                'class': 'Class',
                'id': 'ID',
                'created': 'created',
                'edited': 'edited',
            })
        )

        self.assertEqual(r.hash, 'hash')
        self.assertEqual(r.class_, 'Class')
        self.assertEqual(r.id, 'ID')
        self.assertEqual(r.created, 'created')
        self.assertEqual(r.edited, 'edited')

    def test_content(self):
        r = self._make_one(MockDocument(content={'a': 'a', 'b': 'b'}))
        self.assertEqual(r.content.a, 'a')
        self.assertEqual(r.content.b, 'b')

    def test_attr_error(self):
        r = self._make_one(MockDocument())
        self.assertRaises(AttributeError, getattr, r.content, 'not_found')
        self.assertRaises(AttributeError, getattr, r, 'edited')
