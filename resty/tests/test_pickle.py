import unittest2 as unittest


class TestPropertiesPickle(unittest.TestCase):

    def _get_target(self):
        from resty.documents import Properties
        return Properties

    def _make_one(self):
        return self._get_target()({})

    def test_pickable(self):
        import pickle
        pickle.loads(pickle.dumps(self._make_one()))


class TestLazyPropertiesPickle(TestPropertiesPickle):

    def _get_target(self):
        from resty.documents import LazyProperties
        return LazyProperties
