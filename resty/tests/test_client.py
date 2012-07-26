import unittest2 as unittest

from resty.tests.mocks import MockHttpLoader, MockDocument


class TestClient(unittest.TestCase):

    def _get_target(self):
        from resty import Client
        return Client

    def _make_one(self, loader):
        return self._get_target()(loader.load)

    def test_load_document(self):

        loader = MockHttpLoader()
        loader.register('test://load_document/1/', 'type1', 'text1')
        loader.register('test://load_document/2/', 'type2', 'text2')

        c = self._make_one(loader)

        class Mock(object):
            def __init__(self, client, text):
                self.client = client
                self.text = text

        class Mock1(Mock):
            pass

        class Mock2(Mock):
            pass

        c.register_document_parser('type1', Mock1)
        c.register_document_parser('type2', Mock2)

        d = c.load_document('test://load_document/1/')
        self.assertEqual(d.client, c)
        self.assertEqual(d.text, 'text1')
        self.assertTrue(isinstance(d, Mock1))

        d = c.load_document('test://load_document/2/')
        self.assertEqual(d.client, c)
        self.assertEqual(d.text, 'text2')
        self.assertTrue(isinstance(d, Mock2))

    def test_specialize(self):

        loader = MockHttpLoader()
        c = self._make_one(loader)

        class Mock(object):
            def __init__(self, doc):
                self.doc = doc

        class Mock1(Mock):
            pass

        class Mock2(Mock):
            pass

        c.register_document('type1', Mock1)
        c.register_document('type2', Mock2)

        doc1 = MockDocument(meta={'type': 'type1'})
        doc2 = MockDocument(meta={'type': 'type2'})

        s1 = c.specialize(doc1)
        self.assertTrue(isinstance(s1, Mock1))
        self.assertEqual(s1.doc, doc1)

        s2 = c.specialize(doc2)
        self.assertTrue(isinstance(s2, Mock2))
        self.assertEqual(s2.doc, doc2)
