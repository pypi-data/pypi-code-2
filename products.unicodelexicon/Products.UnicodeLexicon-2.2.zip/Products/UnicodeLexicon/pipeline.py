
import re
import unicodedata

from zope.component import queryUtility
from Products.UnicodeLexicon.interfaces import IDefaultEncoding

from Products.ZCTextIndex.StopDict import get_stopdict
from Products.UnicodeLexicon import accentdata

# Default encoding
defaultEncoding = 'utf-8'


def getDefaultEncoding():
    """Allow to override the default encoding in ZCML."""
    return queryUtility(IDefaultEncoding) or defaultEncoding


class UnicodeWordSplitter:

    word = re.compile(r"(?u)\w+")
    wordGlob = re.compile(r"(?u)\w+[\w*?]*")
    html = re.compile(r"(?u)<[^<>]*>|&[A-Za-z0-9#]+;")

    def process(self, lst, glob=False, strip_html=False):
        result = []
        for w in lst:
            if not isinstance(w, unicode):
                w = unicode(w, getDefaultEncoding())
            if strip_html:
                w = self.html.sub(u' ', w)
            if glob:
                result += self.wordGlob.findall(w)
            else:
                result += self.word.findall(w)
        return result

    def processGlob(self, lst):
        return self.process(lst, True)


class UnicodeHTMLWordSplitter(UnicodeWordSplitter):

    def process(self, lst, glob=False):
        return UnicodeWordSplitter.process(self, lst, glob, True)


class UnicodeCaseNormalizer:

    def process(self, lst):
        result = []
        for w in lst:
            if not isinstance(w, unicode):
                w = unicode(w, getDefaultEncoding())
            result.append(w.lower())
        return result


class UnicodeSingleCharRemover:

    def process(self, lst):
        result = []
        for w in lst:
            if not isinstance(w, unicode):
                w = unicode(w, getDefaultEncoding())
            if len(w) > 1:
                result.append(w)
        return result


class UnicodeStopWordRemover:

    dict = {}
    for k in get_stopdict():
        if not isinstance(k, unicode):
            k = unicode(k, getDefaultEncoding())
        dict[k] = None

    def process(self, lst):
        result = []
        for w in lst:
            if not isinstance(w, unicode):
                w = unicode(w, getDefaultEncoding())
            if not self.dict.has_key(w):
                result.append(w)
        return result


class UnicodeStopWordAndSingleCharRemover(UnicodeStopWordRemover):

    def process(self, lst):
        result = []
        for w in lst:
            if not isinstance(w, unicode):
                w = unicode(w, getDefaultEncoding())
            if len(w) > 1 and not self.dict.has_key(w):
                result.append(w)
        return result


class UnicodeAccentNormalizer:

    accents = {}

    def process(self, lst):
        result = []
        for w in lst:
            if not isinstance(w, unicode):
                w = unicode(w, getDefaultEncoding())
            result.append(w.translate(self.accents))
        return result


class UnicodeLatinAccentNormalizer(UnicodeAccentNormalizer):
    accents = accentdata.LATIN_ACCENTS


class UnicodeGermanAccentNormalizer(UnicodeAccentNormalizer):
    accents = accentdata.GERMAN_ACCENTS

