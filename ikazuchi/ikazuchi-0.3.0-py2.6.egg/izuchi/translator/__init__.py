# -*- coding: utf-8 -*-

import abc

from google import GoogleTranslator
from microsoft import MicrosoftTranslator
from yahoo import YahooTranslator

__all__ = [
    "TRANSLATE_API",
]

class Translator(object):
    """Base class for Translator"""

    __metaclass__ = abc.ABCMeta
    api = lambda klass: klass.__class__.__name__.replace('Translating', '')

    @abc.abstractmethod
    def __init__(self, lang_from, lang_to, handler):
        """Overridden by MixIn class
        must be set "self.handler = handler"
        """

    @abc.abstractmethod
    def detect(self, text): pass

    @abc.abstractmethod
    def translate(self, text): pass

    def call_method_with_handler(self):
        method = getattr(self, self.handler.method_name)
        self.handler._call_method(method)

class AllTranslator(object):
    """Class included in all translators for comparison"""
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.translators = [
            TranslatingGoogle(lang_from, lang_to, handler),
            TranslatingMicrosoft(lang_from, lang_to, handler),
            TranslatingYahoo(lang_from, lang_to, handler),
        ]

    def detect(self, text):
        for t in self.translators:
            for lang in t.detect(text):
                yield lang

    def translate(self, text):
        for t in self.translators:
            for translated in t.translate(text):
                yield translated


# MixIn each implemented Translator
class TranslatingGoogle(GoogleTranslator, Translator): pass
class TranslatingMicrosoft(MicrosoftTranslator, Translator): pass
class TranslatingYahoo(YahooTranslator, Translator): pass
class TranslatingAll(AllTranslator, Translator): pass

TRANSLATE_API = {
    "google": TranslatingGoogle,
    "microsoft": TranslatingMicrosoft,
    "yahoo": TranslatingYahoo,
    "all": TranslatingAll,
}
