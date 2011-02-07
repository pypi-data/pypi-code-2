# -*- coding: utf-8 -*-

import abc
import json
import urllib2
from contextlib import closing
from urllib import urlencode
from xml.etree import ElementTree as ET

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
    def translate(self, text): pass

    def translate_with_handler(self):
        """handler must be implement _translate method"""
        self.handler._translate(self.translate)


class GoogleTranslator(object):
    """
    Translator with Google Translate API
    http://code.google.com/intl/ja/apis/language/translate/overview.html
    see also
    Google Translate API Terms of Use
    http://code.google.com/intl/ja/apis/language/translate/terms.html
    """
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.query = {
            "v": "1.0",
            "langpair": "{0}|{1}".format(lang_from, lang_to),
        }
        domain = "ajax.googleapis.com"
        path = "/ajax/services/language/translate?"
        self._url = "http://{0}{1}".format(domain, path)

    def translate(self, text):
        translated = ""
        self.query.update(q=text.encode("utf-8"))
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            if res_json["responseStatus"] == 200:
                translated = res_json["responseData"]["translatedText"]
            else:
                raise RuntimeError(res_json)
        yield self.api(), translated


class MicrosoftTranslator(object):
    """
    Microsoft Translator
    http://www.microsofttranslator.com/dev/
    see also
    Microsoft Terms of Use
    http://www.bing.com/developers/tou.aspx
    """
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.query = {
            "appId": "D9D0E326A70EA4E66218F43130890052808A0142",
            "from": "{0}".format(lang_from),
            "to": "{0}".format(lang_to),
            "contentType": "text/plain",
            "category": "general",
        }
        domain = "api.microsofttranslator.com"
        path = "/V2/Http.svc/Translate?"
        self._url = "http://{0}{1}".format(domain, path)

    def translate(self, text):
        translated = ""
        self.query.update(text=text.encode("utf-8"))
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            element = ET.parse(res)
            translated = element.getroot().text
        yield self.api(), translated


class YahooTranslator(object):
    """
    Translator with Yahoo! Pipes
    http://pipes.yahoo.com/pipes/
    see also
    Yahoo! Pipes Terms of Use
    http://info.yahoo.com/legal/us/yahoo/pipes/pipes-4396.html
    """
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.query = {
            "_render": "json",
        }
        domain = "pipes.yahoo.com"
        path = "/t2y1979/{0}?".format(self._get_api(lang_from, lang_to))
        self._url = "http://{0}{1}".format(domain, path)

    def _get_api(self, lang_from, lang_to):
        # convert for for arbitrary api name
        api = "{0}2{1}".format(lang_from, lang_to)
        if lang_from == "ja" and lang_to == "en":
            api = "ja2en_"
        elif lang_from == "en" and lang_to.lower() == "zh-cn":
            api = "en2zhcn"
        elif lang_from == "en" and lang_to.lower() == "zh-tw":
            api = "en2zhtw"
        return api

    def translate(self, text):
        translated = ""
        self.query.update(text=text.encode("utf-8"))
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            translated = res_json["value"]["items"][0]["description"]
        yield self.api(), translated


class AllTranslator(object):
    """Class included in all translators for comparison"""
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.translators = [
            TranslatingGoogle(lang_from, lang_to, handler),
            TranslatingMicrosoft(lang_from, lang_to, handler),
            TranslatingYahoo(lang_from, lang_to, handler),
        ]

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
