# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.handler.pofile import *

def test_markup_msgid_notranslate():
    from data.po.markup_notranslate import DATA_SET
    _fmt = u"{0}_{1} ({2} ...)"
    _func = u"test_markup_msgid_notranslate"
    for num, (data, expected) in enumerate(DATA_SET):
        name = _fmt.format(_func, num, str(data)[:10])
        _assert = lambda e, a: assert_equal(e, a)
        _assert.description = name
        yield _assert, expected, POFileHandler.markup_msgid_notranslate(data)
