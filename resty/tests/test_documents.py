import unittest2 as unittest
import json


from resty.tests.mocks import MockStateMachine


class TestJsonDocument(unittest.TestCase):

    def setUp(self):
        self.mock_sm = MockStateMachine()
        self.sentinel = object()
        self.mock_sm.add_document('test://a/b/', self.sentinel)
        self.mock_sm.add_document('test://test/', self.sentinel)

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
            content={'a': [1, 'a'], 'b': {'x': 'x', 1: 1}}
        )
        self.assertEqual(d.content.a, [1, 'a'])
        self.assertEqual(d.content.b, {'x': 'x', 1: 1})
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
                'type': 'type',
                'self': 'self',
                'links': [
                    self._doc_repr(
                        meta={
                            'type': 'T', 'self': 'self',
                            'relationship': 'r1', 'b': 'b',
                        },
                        content={'a': 'a'}
                    ),
                    self._doc_repr(
                        meta={
                            'type': 'T', 'self': 'self',
                            'relationship': 'r2', 'class': 'C1',
                        },
                        content={'c': 1}
                    ),
                    self._doc_repr(
                        meta={
                            'type': 'T', 'self': 'self',
                            'relationship': 'r2', 'class': 'C2',
                        },
                        content={'c': 2}
                    ),
                ],
            },
        )

        rel_doc = d.related('r1')
        self.assertEqual(rel_doc.content.a, 'a')
        self.assertEqual(rel_doc.meta.b, 'b')

        self.assertRaises(ValueError, d.related, 'r2')
        rel_doc = d.related('r2', 'C1')
        self.assertEqual(rel_doc.content.c, 1)
        self.assertEqual(rel_doc.meta.class_, 'C1')
        rel_doc = d.related('r2', 'C2')
        self.assertEqual(rel_doc.content.c, 2)
        self.assertEqual(rel_doc.meta.class_, 'C2')

    def test_services(self):
        d = self._make_one(
            meta={
                'type': 'type',
                'self': 'self',
                'services': {
                    'service1': self._doc_repr(
                        meta={'type': 'T', 'self': 'self'}, content={'s': 1}
                    ),
                    'service2': self._doc_repr(
                        meta={'type': 'T', 'self': 'self'}, content={'s': 2}
                    ),
                }
            },
        )

        serv_doc = d.service('service1')
        self.assertEqual(serv_doc.content.s, 1)
        serv_doc = d.service('service2')
        self.assertEqual(serv_doc.content.s, 2)
        self.assertRaises(ValueError, d.service, 'service3')

    def test_items(self):
        d = self._make_one(
            meta={
                'type': 'type',
                'self': 'self',
                'items': [1, 2, 3],
            },
        )

        self.assertEqual(set(d.get_items()), set([1, 2, 3]))

# from resty.tests.mocks import MockStateMachine, MockDocument

# class TestLazyDocument(unittest.TestCase):

#     def setUp(self):
#         self.sm = MockStateMachine()
#         doc = MockDocument(meta={'b': 'b'}, content={'a': 'a', 'x': 'x'})
#         self.sm.add_state('test://partial_object', doc)

#     def _get_target(self):
#         from resty.documents import LazyDocument
#         return LazyDocument

#     def _make_one(self, meta={}, content={}):
#         meta_copy = dict(('$%s' % key, value) for key, value in meta.items())
#         meta_copy.update(content)
#         return self._get_target()(meta_copy, self.sm)

#     def test_no_attrs(self):
#         d = self._make_one(
#             meta={'type': 'T', 'self': 'test://partial_object'}
#         )
#         self.assertEqual(d.content.a, 'a')
#         self.assertEqual(d.meta.b, 'b')

#     def test_existing_attrs(self):
#         d = self._make_one(
#             meta={'type': 'T', 'self': 'test://partial_object', 'b': 'bb'},
#             content={'a': 'aa'}
#         )
#         self.assertEqual(d.content.a, 'aa')
#         self.assertEqual(d.meta.b, 'bb')
#         self.assertEqual(d.content.x, 'x')  # Trigger rerfesh
#         self.assertEqual(d.content.a, 'a')
#         self.assertEqual(d.meta.b, 'b')

#     def test_attr_error(self):
#         d = self._make_one(
#             meta={'type': 'T', 'self': 'test://partial_object', 'b': 'bb'},
#             content={'a': 'aa'}
#         )
#         self.assertRaises(AttributeError, getattr, d.content, 'not_found')
#         self.assertRaises(AttributeError, getattr, d.meta, 'not_found')
#         self.assertRaises(AttributeError, getattr, d.meta, 'a')
#         self.assertRaises(AttributeError, getattr, d.content, 'b')
