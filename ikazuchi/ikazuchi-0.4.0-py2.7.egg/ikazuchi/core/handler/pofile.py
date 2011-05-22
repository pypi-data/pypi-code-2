# -*- coding: utf-8 -*-

import polib
import re
from base import BaseHandler

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

_NOTRANSLATE_PTRN = re.compile(r"""(
      ["|']*(%|%(.+?))[d|r|s]["|']*
)""", re.U | re.X)

class POFileHandler(BaseHandler):
    """
    Handler class for translating PO file interactively
    """
    max_query = 100

    def __init__(self, api, po_file, encoding):
        if api == "microsoft":
            self.method_name = "translate_array"
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

    def _call_method(self, api_method):
        """translate msgid in po file"""
        _prompt = _(u"Input: ").encode(self.encoding[0])
        for pos in range(0, len(self.po), self.max_query):
            sliced_po = self.po[pos:pos + self.max_query]
            items = [self.markup_msgid_notranslate(p.msgid) for p in sliced_po]
            api, ref = api_method(items)
            _reference = _(u"reference({0}):").format(api)
            for num, p in enumerate(sliced_po):
                _ref = ref[num]
                print u"{0:25}{1}".format(_(u"msgid:"), p.msgid)
                if p.msgstr:
                    print u"{0:25}{1}".format(_(u"current msgstr:"), p.msgstr)
                print u"{0:25}{1}".format(_reference, _ref)
                entered = unicode(raw_input(_prompt), self.encoding[0])
                p.msgstr = self._select_translation(_ref, p.msgstr, entered)
                self.po.save()
                print u"{0:25}{1}".format(_(u"updated msgstr:"), p.msgstr)
                print ""

    @classmethod
    def markup_msgid_notranslate(self, msgid):
        msgid = msgid.replace(u"&", u"&amp;")
        msgid = msgid.replace(u"<", u"&lt;")
        msgid = msgid.replace(u">", u"&gt;")
        repl = r"<span class=notranslate>\1</span>"
        return re.sub(_NOTRANSLATE_PTRN, repl, msgid)
