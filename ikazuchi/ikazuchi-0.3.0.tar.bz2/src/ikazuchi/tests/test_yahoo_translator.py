# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.izuchi.translator import TranslatingYahoo

class TestYahooTranslator(object):

    def setup(self):
        self.t = TranslatingYahoo("ja", "en", None)

    def test_get_api_path(self):
        def translate(): pass

        assert_equal("ja2en_?", self.t.get_api_path(translate))

    def test_detect(self):
        res = list(self.t.detect(unicode("テスト", "utf-8")))
        assert_equal(u"Not Supported", res[0][1])

    def test_translate(self):
        assert_equal([('Yahoo', u'Test')],
                     list(self.t.translate(unicode("テスト", "utf-8"))))
