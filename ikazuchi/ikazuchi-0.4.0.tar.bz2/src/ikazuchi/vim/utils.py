# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    pass

def to_unicode(seq, enc):
    return [unicode(i, enc) for i in seq]

def to_encode(seq, enc):
    return [i.encode(enc) for i in seq]

def get_vim_variables():
    # settings from VimScript(.vimrc)
    try:
        api_name = vim.eval("raimei_api")
        lang_from = vim.eval("raimei_from")
        lang_to = vim.eval("raimei_to")
        enc = vim.eval("&enc")
    except vim.error:
        #  vim.error is String Exception
        print "Set enc, raimei_api, raimei_from, raimei_to variables!"
        raise
    return api_name, lang_from, lang_to, enc
