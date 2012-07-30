import unittest2 as unittest
import json


from resty.tests.mocks import MockStateMachine, MockDocument
from resty.documents import DocumentError


class TestJsonDocument(unittest.TestCase):

    def setUp(self):
        self.mock_sm = MockStateMachine()

        mock_d = MockDocument(
            meta={
                'type': 'T',
                'self': 'test://mock_resource/1/',
                'class': 'C1',
                'a': 'a', 'x': 'x',
            },
            content={'b': 'b', 'y': 'y'},
        )
        self.mock_sm.add_document(mock_d.self, mock_d)

        mock_d = MockDocument(
            meta={
                'type': 'T',
                'self': 'test://mock_resource/2/',
                'class': 'C2',
                'a': 'a', 'x': 'x',
            },
            content={'b': 'b', 'y': 'y'},
        )
        self.mock_sm.add_document(mock_d.self, mock_d)

        mock_d = MockDocument(
            meta={
                'type': 'T',
                'self': 'test://mock_resource/3/',
                'class': 'C3',
                'a': 'a', 'x': 'x',
            },
            content={'b': 'b', 'y': 'y'},
        )
        self.mock_sm.add_document(mock_d.self, mock_d)

        self.sentinel = object()
        self.mock_sm.add_document('test://a/b/', self.sentinel)
        self.mock_sm.add_document('test://test/', self.sentinel)
        self.mock_sm.add_document('test://test/1/', self.sentinel)
        self.mock_sm.add_document('test://test/2/', self.sentinel)

    def _get_target(self):
        from resty.documents import JsonDocument
        return JsonDocument

    def _make_one(self, meta={}, content={}):
        data = json.dumps(self._doc_repr(meta, content))
        return self._get_target()(self.mock_sm, data)

    def _doc_repr(self, meta={}, content={}):
        meta_copy = dict(('$%s' % key, value) for key, value in meta.items())
        meta_copy.update(content)
        return meta_copy

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
        self.assertRaises(AttributeError, getattr, d.meta, 'type')
        self.assertRaises(AttributeError, getattr, d.meta, 'self')

    def test_meta_attrs(self):
        d = self._make_one(
            meta={'type': 'type', 'self': 'self', 'a': 'a', 'b': 'b'}
        )
        self.assertEqual(d.meta.a, 'a')
        self.assertEqual(d.meta.b, 'b')

    def test_content_attrs(self):
        d = self._make_one(
            meta={'type': 'type', 'self': 'self'}, content={'a': 'a', 'b': 'b'}
        )
        self.assertEqual(d.content.a, 'a')
        self.assertEqual(d.content.b, 'b')

    def test_attr_errors(self):
        d = self._make_one(
            meta={'type': 'type', 'self': 'self', 'a': 'a'}, content={'b': 'b'}
        )
        self.assertEqual(d.meta.a, 'a')
        self.assertEqual(d.content.b, 'b')
        self.assertRaises(AttributeError, getattr, d.content, 'a')
        self.assertRaises(AttributeError, getattr, d.meta, 'b')

    def test_complex_structure(self):
        d = self._make_one(
            meta={'type': 'type', 'self': 'self'},
            content={'a': [1, 'a'], 'b': {'x': 'x', 'y': 1}}
        )
        self.assertEqual(d.content.a, [1, 'a'])
        self.assertEqual(d.content.b, {'x': 'x', 'y': 1})
        self.assertRaises(AttributeError, getattr, d.content.b, 'x')

    def test_class_meta(self):
        d = self._make_one(
            meta={'type': 'type', 'self': 'self', 'class': 'C'},
        )
        self.assertEqual(d.meta.class_, 'C')

    def test_filters(self):
        d = self._make_one(
            meta={
                'type': 'type',
                'self': 'self',
                'filters': {
                    'filter1': 'test://{placeholder1}/{placeholder2}/',
                    'filter2': 'test://test/',
                },
            },
        )

        f = d.filter('filter1', placeholder1='a', placeholder2='b')
        self.assertEqual(f, self.sentinel)

        f = d.filter('filter2')
        self.assertEqual(f, self.sentinel)

    def test_links(self):
        d = self._make_one(
            meta={
                'type': 'type', 'self': 'self',
                'links': [
                    self._doc_repr(
                        meta={
                            'type': 'T', 'self': 'test://mock_resource/1/',
                            'relationship': 'R1', 'class': 'C1',
                            'a': 'a',
                        },
                        content={'b': 'b'}
                    ),
                    self._doc_repr(
                        meta={
                            'type': 'T', 'self': 'test://mock_resource/2/',
                            'relationship': 'R2', 'class': 'C2',
                        }
                    ),
                    self._doc_repr(
                        meta={
                            'type': 'T', 'self': 'test://mock_resource/3/',
                            'relationship': 'R2', 'class': 'C3',
                        }
                    ),
                ],
            },
        )

        rel_doc = d.related('R1')
        self.assertEqual(rel_doc.meta.class_, 'C1')
        self.assertEqual(rel_doc.meta.a, 'a')
        self.assertEqual(rel_doc.meta.x, 'x')
        self.assertEqual(rel_doc.content.b, 'b')
        self.assertEqual(rel_doc.content.y, 'y')

        self.assertRaises(ValueError, d.related, 'R2')
        rel_doc = d.related('R2', 'C2')
        self.assertEqual(rel_doc.meta.class_, 'C2')
        rel_doc = d.related('R2', 'C3')
        self.assertEqual(rel_doc.meta.class_, 'C3')

    def test_services(self):
        d = self._make_one(
            meta={
                'type': 'type',
                'self': 'self',
                'services': {
                    'service1': self._doc_repr(
                        meta={'type': 'T', 'self': 'test://mock_resource/1/'}
                    ),
                    'service2': self._doc_repr(
                        meta={'type': 'T', 'self': 'test://mock_resource/2/'}
                    ),
                }
            },
        )

        serv_doc = d.service('service1')
        self.assertEqual(serv_doc.meta.a, 'a')
        self.assertEqual(serv_doc.content.b, 'b')
        self.assertEqual(serv_doc.meta.class_, 'C1')
        serv_doc = d.service('service2')
        self.assertEqual(serv_doc.meta.a, 'a')
        self.assertEqual(serv_doc.content.b, 'b')
        self.assertEqual(serv_doc.meta.class_, 'C2')
        self.assertRaises(ValueError, d.service, 'service3')

    def test_items(self):
        d = self._make_one(
            meta={
                'type': 'type',
                'self': 'self',
                'items': [
                    self._doc_repr(
                        meta={'type': 'T', 'self': 'test://mock_resource/1/'}
                    ),
                    self._doc_repr(
                        meta={'type': 'T', 'self': 'test://mock_resource/2/'}
                    ),
                    self._doc_repr(
                        meta={'type': 'T', 'self': 'test://mock_resource/3/'}
                    ),
                ],
            },
        )

        item_docs = list(d.items())
        self.assertEqual(item_docs[0].meta.class_, 'C1')
        self.assertEqual(item_docs[1].meta.class_, 'C2')
        self.assertEqual(item_docs[2].meta.class_, 'C3')

    def test_page(self):
        d = self._make_one(
            meta={
                'type': 'type',
                'self': 'self',
                'page_control': 'test://test/{page_num}/',
            },
        )

        self.assertEqual(d.page(1), self.sentinel)
        self.assertEqual(d.page(2), self.sentinel)

    def test_specialize(self):
        d = self._make_one(meta={'type': 'T', 'self': 'self'})
        self.assertEqual(d.specialize(), 'specialized T')

    def test_error(self):
        d = self._make_one(meta={'type': 'T', 'self': 'self'})

        self.assertRaises(DocumentError, d.related, 'R')
        self.assertRaises(DocumentError, d.service, 'S')
        self.assertRaises(DocumentError, d.items)
        self.assertRaises(DocumentError, d.page, 1)
        self.assertRaises(DocumentError, d.filter, 'F')


class TestLazyDocument(unittest.TestCase):

    def setUp(self):
        self.mock_sm = MockStateMachine()

        self.registered_d = MockDocument(
            meta={
                'type': 'T',
                'self': 'test://mock_resource/',
                'class': 'C1',
                'a': 'a', 'x': 'x',
            },
            content={'b': 'b', 'y': 'y'},
        )
        self.mock_sm.add_document(self.registered_d.self, self.registered_d)

        self.d = MockDocument(
            meta={
                'type': 'T', 'self': 'test://mock_resource/',
                'a': 'aa',
            },
            content={'b': 'bb'}
        )

    def _get_target(self):
        from resty.documents import LazyDocument
        return LazyDocument

    def _make_one(self, doc):
        return self._get_target()(self.mock_sm, doc)

    def test_fast_accesss(self):
        ld = self._make_one(self.d)

        self.assertEqual(ld.meta.a, 'aa')
        self.assertEqual(ld.content.b, 'bb')

    def test_slow_accesss(self):
        ld = self._make_one(self.d)

        self.assertEqual(ld.meta.x, 'x')
        self.assertEqual(ld.content.y, 'y')

    def test_reload(self):
        ld = self._make_one(self.d)

        ld.meta.x  # Trigger data reload
        self.assertEqual(ld.meta.a, 'a')
        self.assertEqual(ld.content.b, 'b')

    def test_attr_error(self):
        ld = self._make_one(self.d)

        self.assertRaises(AttributeError, getattr, ld.meta, 'not_existing')
        self.assertRaises(AttributeError, getattr, ld.content, 'not_existing')

    def test_deferred_related(self):
        sentinel = object()
        self.registered_d.add_related('R', sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.related('R'), sentinel)

    def test_deferred_service(self):
        sentinel = object()
        self.registered_d.add_service('S', sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.service('S'), sentinel)

    def test_deferred_items(self):
        sentinel = object()
        self.registered_d.add_item(sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.items(), [sentinel])

    def test_deferred_page(self):
        sentinel = object()
        self.registered_d.add_page(1, sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.page(1), sentinel)

    def test_deferred_filter(self):
        sentinel = object()
        self.registered_d.add_filter('F', sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.filter('F'), sentinel)

    def test_fast_related(self):
        sentinel = object()
        self.d.add_related('R', sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.related('R'), sentinel)

    def test_fast_service(self):
        sentinel = object()
        self.d.add_service('S', sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.service('S'), sentinel)

    def test_fast_items(self):
        sentinel = object()
        self.d.add_item(sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.items(), [sentinel])

    def test_fast_page(self):
        sentinel = object()
        self.d.add_page(1, sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.page(1), sentinel)

    def test_fast_filter(self):
        sentinel = object()
        self.registered_d.add_filter('F', sentinel)
        d = self._make_one(self.d)

        self.assertEqual(d.filter('F'), sentinel)
