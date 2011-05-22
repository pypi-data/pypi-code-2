# -*- coding: utf-8 -*-

import abc
import re
import utils
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
    # FIXME: span tag only, cannot match for minimal when html tag is nested
    notrans_tag = re.compile(
        r"<span class=[\"']?notranslate[\"']?>(.*?)</span>", re.IGNORECASE)
    whitespaces = re.compile(r"\s+", re.UNICODE)
    zerowidth = re.compile(u"\u200b|\u200c|\u200d|\ufeff", re.UNICODE)

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

    def parse_html(self, html):
        from StringIO import StringIO
        from formatter import (AbstractFormatter, DumbWriter)
        from htmllib import HTMLParser
        _html = re.sub(self.notrans_tag, r" \1 ", html)
        buf = StringIO()
        p = HTMLParser(AbstractFormatter(DumbWriter(buf)))
        p.feed(_html)
        _ret = re.sub(self.whitespaces, " ", buf.getvalue())
        # FIXME: how can zerowidth be removed more simply?
        return re.sub(self.zerowidth, "", _ret)

# MixIn each implemented Translator
class TranslatingGoogle(GoogleTranslator, Translator): pass
class TranslatingMicrosoft(MicrosoftTranslator, Translator): pass
class TranslatingYahoo(YahooTranslator, Translator): pass  # is obsoleted

TRANSLATE_API = {
    "google": TranslatingGoogle,
    "microsoft": TranslatingMicrosoft,
}
