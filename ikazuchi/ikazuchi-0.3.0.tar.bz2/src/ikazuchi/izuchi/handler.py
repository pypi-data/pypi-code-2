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


class BaseHandler(object):
    """Base class for handler"""

    __metaclass__ = abc.ABCMeta

    method_name = "translate"

    @abc.abstractmethod
    def _call_method(self, method): pass

class POFileHandler(BaseHandler):
    """
    Handler class for translating interactively
    """
    def __init__(self, po_file, encoding):
        self.encoding = encoding
        self.po = polib.pofile(po_file, autodetect_encoding=False,
                               encoding=self.encoding[1])
        self.po.metadata["Content-Type"] = "text/plain; charset={0}".format(
                                                self.encoding[1])

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

    def _call_method(self, translate):
        """translate msgid in po file"""
        _prompt = _(u"Input: ").encode(self.encoding[0])
        for p in self.po:
            api, ref = self._get_translated_text(p.msgid, translate)
            print _(u"msgid:\t\t\t{0}").format(p.msgid)
            if p.msgstr:
                print _(u"current msgstr:\t\t{0}").format(p.msgstr)
            print _(u"reference({0}):\t{1}").format(api, ref)
            entered = unicode(raw_input(_prompt), self.encoding[0])
            p.msgstr = self._select_translation(ref, p.msgstr, entered)
            self.po.save()
            print _(u"updated msgstr:\t\t{0}").format(p.msgstr)
            print ""

class SingleSentenceHandler(BaseHandler):
    """
    Handler class for translating single sentence
    """
    def __init__(self, opts):
        self.sentence = opts.sentence
        self.encoding = opts.encoding
        self.quiet = opts.quiet
        if opts.detect:
            self.method_name = "detect"

    def _encode(self, text):
        return text.encode(self.encoding[1])

    def _call_method(self, api_method):
        if not self.quiet:
            print self._encode(u"{0:25}{1}".format("sentence:", self.sentence))
        for api, result in api_method(self.sentence):
            _method = u"{0}({1}):".format(self.method_name, api)
            print self._encode(u"{0:25}{1}".format(_method, result))
