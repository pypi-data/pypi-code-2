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
        h = POFileHandler(opts.po_file, opts.encoding)
    elif opts.sentence:
        h = SingleSentenceHandler(opts)
    return h

def get_encoding(option, opt_str, value, parser):
    enc = "".join(value.split()).split(",")
    enc_out = enc[1:] and enc[1] or enc[0]
    parser.values.encoding = [enc[0], enc_out]

def check_encoding(encoding):
    ret = []
    for enc in encoding:
        try:
            unicode("test", enc)
        except LookupError:
            ret.append(enc)
    return ret

def set_default_encoding(opts):
    from locale import getdefaultlocale
    enc = getdefaultlocale()[1]
    opts.encoding = [enc, enc]

def convrt_str_to_unicode(opts):
    if opts.sentence:
        opts.sentence = unicode(opts.sentence, opts.encoding[0])

_UNSUPPORTED_VERSION = _("Unsupported Python version, use 2.6 above")

def check_python_version():
    ver = sys.version_info
    if ver[0] == 2 and ver[1] < 6:
        print _UNSUPPORTED_VERSION
        sys.exit(0)
