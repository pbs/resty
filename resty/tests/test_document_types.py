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
        self.assertEqual(r.related('relationship2'), 'specialized R2')


class TestService(unittest.TestCase):

    def _get_target(self):
        from resty.types import Service
        return Service

    def _make_one(self, doc):
        return self._get_target()(doc)

    def test_known_meta(self):
        r = self._make_one(MockDocument(meta={'self': 'S', 'hash': 'hash'}))

        self.assertEqual(r.self, 'S')
        self.assertEqual(r.hash, 'hash')

    def test_content(self):
        r = self._make_one(MockDocument(content={'a': 'a', 'b': 'b'}))
        self.assertEqual(r.content.a, 'a')
        self.assertEqual(r.content.b, 'b')

    def test_attr_error(self):
        r = self._make_one(MockDocument())
        self.assertRaises(AttributeError, getattr, r.content, 'not_found')
        self.assertRaises(AttributeError, getattr, r, 'edited')

    def test_get_related(self):
        doc = MockDocument(
            meta={'type': 'T', 'self': 'test://document/'}
        )
        doc.add_service('s1',
            MockDocument(meta={'type': 'R1', 'self': 'test://related'})
        )
        doc.add_service('s2',
            MockDocument(meta={'type': 'R2', 'self': 'test://related'})
        )
        r = self._make_one(doc)
        self.assertEqual(r.service('s1'), 'specialized R1')
        self.assertEqual(r.service('s2'), 'specialized R2')


class TestCollection(unittest.TestCase):

    def _get_target(self):
        from resty.types import Collection
        return Collection

    def _make_one(self, doc):
        return self._get_target()(doc)

    def test_known_meta(self):
        r = self._make_one(MockDocument(meta={
            'self': 'S',
            'elements': 'ET',
            'hash': 'hash',
        }))

        self.assertEqual(r.self, 'S')
        self.assertEqual(r.elements, 'ET')
        self.assertEqual(r.hash, 'hash')

    def test_attr_error(self):
        r = self._make_one(MockDocument(meta={'elements': 'ET'}))
        self.assertRaises(AttributeError, getattr, r, 'hash')

    def test_filter(self):
        doc = MockDocument(meta={'elements': 'ET'})
        doc.add_filter('zipcode', MockDocument(meta={'type': 'ZIP'}))
        doc.add_filter('IP', MockDocument(meta={'type': 'IP'}))
        r = self._make_one(doc)
        self.assertEqual(r.filter('zipcode'), 'specialized ZIP')
        self.assertEqual(r.filter('IP'), 'specialized IP')
        self.assertRaises(ValueError, r.filter, 'err')

    def test_iter_simple(self):
        doc = MockDocument(meta={'elements': 'ET'})
        doc.add_item(MockDocument(meta={'type': 'T1'}))
        doc.add_item(MockDocument(meta={'type': 'T2'}))
        r = self._make_one(doc)
        items = list(r.items())
        self.assertEqual(items, ['specialized T1', 'specialized T2'])

    def test_iter_multi_page(self):

        page1 = MockDocument(meta={'elements': 'ET'})
        page1.add_item(MockDocument(meta={'type': 'T1'}))
        page1.add_item(MockDocument(meta={'type': 'T2'}))

        page2 = MockDocument(meta={'elements': 'ET'})
        page2.add_item(MockDocument(meta={'type': 'T3'}))
        page2.add_item(MockDocument(meta={'type': 'T4'}))

        page3 = MockDocument(meta={'elements': 'ET'})
        page3.add_item(MockDocument(meta={'type': 'T5'}))

        page1.meta.page_size = page2.meta.page_size = page3.meta.page_size = 2
        page1.meta.items_count = page2.meta.items_count = page3.meta.items_count = 5
        page1.meta.page, page2.meta.page, page3.meta.page = 1, 2, 3

        page1.add_page(1, page1)
        page1.add_page(2, page2)
        page1.add_page(3, page3)

        page2.add_page(1, page1)
        page2.add_page(2, page2)
        page2.add_page(3, page3)

        page3.add_page(1, page1)
        page3.add_page(2, page2)
        page3.add_page(3, page3)

        r = self._make_one(page1)
        items = list(r.items())
        self.assertEqual(items, [
            'specialized T1',
            'specialized T2',
            'specialized T3',
            'specialized T4',
            'specialized T5',
        ])
