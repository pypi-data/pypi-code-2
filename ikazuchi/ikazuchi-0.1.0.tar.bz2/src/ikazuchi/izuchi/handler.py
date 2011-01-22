# -*- coding: utf-8 -*-

import abc
import polib

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

__all__ = [
    "POFileHandler",
    "SingleSentenceHandler",
]

DEFAULT_ENCODING = "utf-8"

class BaseHandler(object):
    """Base class for handler"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _translate(self, translate_method): pass

class POFileHandler(BaseHandler):
    """
    Handler class for translating interactively
    """
    def __init__(self, po_file):
        from locale import getdefaultlocale
        self.po = polib.pofile(po_file)
        self.po.metadata["Content-Type"] = "text/plain; charset=utf-8"
        self.encoding = getdefaultlocale()[1]
        if not self.encoding:
            self.encoding = DEFAULT_ENCODING

    def _select_translation(self, ref, current, entered):
        """define which translated string use"""
        s = entered
        if entered.lower() == "y":
            s = ref
        elif current and entered == "":
            s = current
        return s

    def _get_translated_text(self, msgid, translate):
        """safe read since translate method is generator"""
        text = u""
        for api, ref in translate(msgid):
            text += ref
        return api, text

    def _translate(self, translate):
        """translate msgid in po file"""
        _prompt = _(u"Input: ").encode(self.encoding)
        for p in self.po:
            api, ref = self._get_translated_text(p.msgid, translate)
            print _(u"msgid:\t\t\t{0}").format(p.msgid)
            if p.msgstr:
                print _(u"current msgstr:\t\t{0}").format(p.msgstr)
            print _(u"reference({0}):\t{1}").format(api, ref)
            entered = unicode(raw_input(_prompt), self.encoding)
            p.msgstr = self._select_translation(ref, p.msgstr, entered)
            self.po.save()
            print _(u"updated msgstr:\t\t{0}").format(p.msgstr)
            print ""

class SingleSentenceHandler(BaseHandler):
    """
    Handler class for translating single sentence
    """
    def __init__(self, sentence):
        self.sentence = sentence

    def _translate(self, translate):
        print _(u"sentence:\t\t{0}").format(self.sentence)
        for api, text in translate(self.sentence):
            print _(u"translated({0}):\t{1}").format(api, text)
