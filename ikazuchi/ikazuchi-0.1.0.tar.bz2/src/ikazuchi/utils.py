# -*- coding: utf-8 -*-

import sys

from izuchi.handler import *
from locale import _

def get_lang():
    from locale import getdefaultlocale
    lang, country = getdefaultlocale()[0].split("_")
    return lang

def get_handler(opts):
    h = None
    if opts.po_file:
        h = POFileHandler(opts.po_file)
    elif opts.sentence:
        h = SingleSentenceHandler(opts.sentence)
    return h

def convrt_str_to_unicode(opts):
    from locale import getdefaultlocale
    if opts.sentence:
        opts.sentence = unicode(opts.sentence, getdefaultlocale()[1])

_UNSUPPORTED_VERSION = _("Unsupported Python version, use 2.6 above")

def check_python_version():
    ver = sys.version_info
    if ver[0] == 2 and ver[1] < 6:
        print _UNSUPPORTED_VERSION
        sys.exit(0)
