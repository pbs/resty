import unittest2 as unittest

from resty.tests.mocks import MockHttpLoader


class TestClient(unittest.TestCase):

    def _get_target(self):
        from resty import Client
        return Client

    def _make_one(self):
        loader = MockHttpLoader()
        loader.register('test://load_document/1/', 'type1', 'text1')
        loader.register('test://load_document/2/', 'type2', 'text2')
        return self._get_target()(loader.load)

    def test_load_document(self):

        class MockDocument(object):
            def __init__(self, client, text):
                self.client = client
                self.text = text

        class MockDocument1(MockDocument):
            pass

        class MockDocument2(MockDocument):
            pass

        c = self._make_one()
        c.register_document_parser('type1', MockDocument1)
        c.register_document_parser('type2', MockDocument2)

        d = c.load_document('test://load_document/1/')
        self.assertEqual(d.client, c)
        self.assertEqual(d.text, 'text1')
        self.assertTrue(isinstance(d, MockDocument1))

        d = c.load_document('test://load_document/2/')
        self.assertEqual(d.client, c)
        self.assertEqual(d.text, 'text2')
        self.assertTrue(isinstance(d, MockDocument2))
