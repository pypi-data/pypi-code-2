#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

from conf import (get_conf, get_conf_path)
from core.translator import TRANSLATE_API
from locale import _
from utils import *

__version__ = "0.4.2"

def get_args():
    parser = argparse.ArgumentParser()
    parser.set_defaults(api="google", detect=False, lang=False,
                        lang_from="en", lang_to=get_lang(),
                        po_file=None, rst_file=None, sentence=None,
                        encoding=None, quiet=False, verbose=False)
    parser.add_argument("-a", "--api", dest="api", metavar="API",
                        help=u"APIs are {0}".format(TRANSLATE_API.keys()))
    parser.add_argument("-d", "--detect", dest="detect", action="store_true",
                        help=u"detect language for target sentence")
    parser.add_argument("-e", "--encoding", dest="encoding",
                        action=EncodingAction, metavar="ENCODING",
                        help=u"input/output encoding")
    parser.add_argument("-f", "--from", dest="lang_from", metavar="LANG",
                        help=u"original language")
    parser.add_argument("-l", "--languages", dest="lang", action="store_true",
                        help=u"show supported languages")
    parser.add_argument("-p", "--pofile", dest="po_file", nargs=1,
                        metavar="POFILE", help=u"target po file")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                        help=u"not to show original sentence to stdout")
    parser.add_argument("-r", "--rstfile", dest="rst_file", nargs=1,
                        metavar="RSTFILE", help=u"target reST file")
    parser.add_argument("-s", "--sentences", dest="sentences", nargs="+",
                        metavar="SENTENCE", help=u"target sentences")
    parser.add_argument("-t", "--to", dest="lang_to", metavar="LANG",
                        help=u"target language to translate")
    parser.add_argument("--version", action="version",
                        version="%(prog)s {0}".format(__version__))

    opts = parser.parse_args()
    if not opts.lang_to:
        opts.lang_to = raw_input(u"Type language code: ")

    err_msg = None
    if opts.api not in TRANSLATE_API.keys():
        err_msg = _(u"Unsupported API: {0}").format(opts.api)
    elif opts.po_file and not os.access(opts.po_file[0], os.R_OK):
        err_msg = _(u"Cannot access po file: {0}").format(opts.po_file[0])
    elif opts.rst_file and not os.access(opts.rst_file[0], os.R_OK):
        err_msg = _(u"Cannot access reST file: {0}").format(opts.rst_file[0])
    elif opts.encoding:
        err_encoding = check_encoding(opts.encoding)
        if err_encoding:
            err_msg = _(u"Unknown encodings: {0}").format(err_encoding)
    elif not (opts.lang or opts.po_file or opts.rst_file or opts.sentences):
        err_msg = _(u"Need to specify optional arguments")

    if err_msg:
        parser.print_help()
        print err_msg
        sys.exit(0)

    if not opts.encoding:
        set_default_encoding(opts)
    convert_str_to_unicode(opts)
    return opts

def main():
    # pre process
    check_python_version()
    conf = get_conf(get_conf_path())
    # main process
    opts = get_args()
    handler = get_handler(opts)
    t = TRANSLATE_API[opts.api](opts.lang_from, opts.lang_to, handler)
    t.set_apikey_from_conf(conf)
    t.call_method_with_handler()

if __name__ == "__main__":
    main()
