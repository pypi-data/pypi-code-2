# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.izuchi.handler import *
from ikazuchi.izuchi.translator import TRANSLATE_API

class TestAllTranslator(object):

    class Option(object):
        sentence = None
        encoding = None
        quiet = False
        detect = False

    def setup(self):
        opts = TestAllTranslator.Option()
        t = TRANSLATE_API["all"]
        self.apis = t("en", "ja", SingleSentenceHandler(opts))
        self.apis_rev = t("ja", "en", SingleSentenceHandler(opts))

    def test_is_exist_handler(self):
        for t in self.apis.translators:
            assert_equals(SingleSentenceHandler, t.handler.__class__)

    def test_call_apis(self):
        for i, translated in enumerate(self.apis.translate("test")):
            expected = (self.apis.translators[i].api(),
                        unicode("テスト", "utf-8"))
            assert_equals(expected, translated)

    def test_call_apis_rev(self):
        text = unicode("テスト", "utf-8")
        for i, translated in enumerate(self.apis_rev.translate(text)):
            expected = (self.apis.translators[i].api(), u"test")
            _translated = translated[0], translated[1].lower()
            assert_equals(expected, _translated)
