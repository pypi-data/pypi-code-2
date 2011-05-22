# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile enrai' from vim"

import izuchi
import sys
from utils import (to_unicode, to_encode, get_vim_variables)

def get_word_on_cursor(enc):
    words = to_unicode(vim.current.line.split(" "), enc)
    cur_row, cur_column = vim.current.window.cursor
    cur_column += 1  # add 1 since cursor column start from 0
    word_pos = 0
    for word in words:
        word_pos += len(word) + 1  # for whitespace
        if cur_column <= word_pos:
            return word
    return None

def translate_with_word(t, enc):
    word = get_word_on_cursor(enc)
    if word:
        ret = t.translate(word)
        vim.command("let enrai_target_word='{0}'".format(word.encode(enc)))
        print "Translated by {0}: {1}".format(*to_encode(ret, enc))

def translate(api_name, lang_from, lang_to, enc):
    t = izuchi.translator.TRANSLATE_API[api_name](lang_from, lang_to, None)
    return translate_with_word(t, enc)

def main():
    try:
        vim_vars = get_vim_variables()
        translate(*vim_vars)
    except Exception as err:
        print err.message
        return

if __name__ == "__main__":
    main()
