# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.izuchi.translator import TranslatingGoogle

class TestGoogleTranslator(object):

    def setup(self):
        self.t = TranslatingGoogle("ja", "en", None)

    def test_get_api_path(self):
        def detect(): pass

        assert_equal("detect?", self.t.get_api_path(detect))

    def test_detect(self):
        res = list(self.t.detect(unicode("テスト", "utf-8")))
        assert_equal(u"ja", res[0][1])

    def test_translate(self):
        assert_equal([('Google', u'Test')],
                     list(self.t.translate(unicode("テスト", "utf-8"))))
