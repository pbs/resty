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
                'self': 'S',
                'hash': 'hash',
                'class': 'Class',
                'id': 'ID',
                'created': 'created',
                'edited': 'edited',
            })
        )

        self.assertEqual(r.self, 'S')
        self.assertEqual(r.hash, 'hash')
        self.assertEqual(r.class_, 'Class')
        self.assertEqual(r.id, 'ID')
        self.assertEqual(r.created, 'created')
        self.assertEqual(r.edited, 'edited')

    def test_content(self):
        r = self._make_one(
            MockDocument(
                meta={'class': 'C'},
                content={'a': 'a', 'b': 'b'}
            )
        )
        self.assertEqual(r.content.a, 'a')
        self.assertEqual(r.content.b, 'b')

    def test_attr_error(self):
        r = self._make_one(MockDocument(meta={'class': 'C'}))
        self.assertRaises(AttributeError, getattr, r.content, 'not_found')
        self.assertRaises(AttributeError, getattr, r, 'edited')

    def test_get_related(self):
        doc = MockDocument(
            meta={'type': 'T', 'self': 'test://document/', 'class': 'C'}
        )
        doc.add_related(
            'relationship1',
            MockDocument(meta={'type': 'R1', 'self': 'test://related'})
        )
        doc.add_related(
            'relationship2',
            MockDocument(meta={'type': 'R2', 'self': 'test://related'})
        )
        r = self._make_one(doc)
        self.assertEqual(r.related('relationship1'), 'specialized R1')
        self.assertEqual(r.related('relationship1'), 'specialized R2')
