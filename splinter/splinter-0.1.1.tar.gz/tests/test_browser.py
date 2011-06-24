import __builtin__
import unittest

class TestBrowser(unittest.TestCase):

    def setUp(self):
        self.old = __builtin__.__import__
        def mocked_import(name, *args, **kwargs):
            if 'zope.testbrowser' in name:
                raise ImportError
            return self.old(name, *args, **kwargs)

        __builtin__.__import__ = mocked_import

    def tearDown(self):
        __builtin__.__import__ = self.old

    def test_should_not_include_zopetestbrowser_when_it_is_not_present(self):
        from splinter import browser
        assert 'zope.testbrowser' not in browser._DRIVERS
