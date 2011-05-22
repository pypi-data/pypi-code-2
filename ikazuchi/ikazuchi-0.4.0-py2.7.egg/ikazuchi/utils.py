# -*- coding: utf-8 -*-

import argparse
import sys

from core.handler import *
from locale import _

def get_lang():
    from locale import getdefaultlocale
    lang, country = getdefaultlocale()[0].split("_")
    return lang

def get_handler(opts):
    h = None
    if opts.lang:
        h = LanguageHandler(opts.api, opts.encoding)
    elif opts.po_file:
        h = POFileHandler(opts.api, opts.po_file[0], opts.encoding)
    elif opts.rst_file:
        h = reSTFileHandler(opts)
    elif opts.sentences:
        # FIXME: consider later about audio handler
        if (opts.sentences[0] == "audio" or opts.sentences[-1] == "audio") \
            and len(opts.sentences) >= 2:
            h = AudioHandler(opts)
        else:
            h = SingleSentenceHandler(opts)
    return h

class EncodingAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        enc = "".join(values.split()).split(",")
        enc_out = enc[1:] and enc[1] or enc[0]
        setattr(namespace, self.dest, [enc[0], enc_out])

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

def convert_str_to_unicode(opts):
    if opts.sentences:
        opts.sentences = [unicode(s, opts.encoding[0]) for s in opts.sentences]

_UNSUPPORTED_VERSION = _("Unsupported Python version, use 2.6 above")

def check_python_version():
    ver = sys.version_info
    if ver[0] == 2 and ver[1] < 6:
        print _UNSUPPORTED_VERSION
        sys.exit(0)
