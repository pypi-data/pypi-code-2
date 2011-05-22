# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile raimei' from vim"

import izuchi
import re
import sys
from os.path import splitext
from utils import (to_unicode, to_encode, get_vim_variables)

_SENTENCE_PATTERN = {
    "en": unicode(r"[\.|\?|!|:][ |$]+", "utf-8"),
    "ja": unicode(r"[。|．|？|！]", "utf-8"),
}

_END_OF_SENTENCE = unicode(r"[\.|\?|:|!|。|．|？|！]$", "utf-8")

# use old API temporally
_v1 = izuchi.translator.google.GoogleTranslatorV1
class TranslatingGoogle(_v1, izuchi.translator.Translator): pass

# just for alias
_translate_api = izuchi.translator.TRANSLATE_API
_translate_api["google"] = TranslatingGoogle
_call_api_with_multithread = izuchi.translator.utils.call_api_with_multithread
_rest_caller = izuchi.handler.rstfile.reSTApiCaller

def remove_imcomplete_line(lines, start, enc):
    prev = vim.current.buffer[start - 1:start]
    if prev and prev[0]:
        if not re.search(_END_OF_SENTENCE, unicode(prev[0].rstrip(), enc)):
            # remove first line if previous line is not end of a sentence
            lines = lines[1:]
    return lines

def get_lines_with_sentence(start, end, enc):
    _buffer = vim.current.buffer[start:end]
    text = u" ".join(unicode(t.strip(), enc) for t in _buffer)
    text += u" "  # FIXME: pattern matching for end with "."

    # get lines for each single sentence
    lines = []
    flags = re.MULTILINE | re.UNICODE
    base_ptrn = _SENTENCE_PATTERN.get(vim.eval("raimei_from")) or \
                _SENTENCE_PATTERN["en"]
    sentence_num = len(re.findall(base_ptrn, text, flags))
    if sentence_num > 0:
        ptrn = u"(.*{0})".format(base_ptrn) * sentence_num
        match = re.findall(ptrn, text, flags)
        # format lines
        if match:
            if isinstance(match[0], tuple):
                lines = remove_imcomplete_line(match[0], start, enc)
                lines = [line.strip().rstrip() for line in lines]
            else:
                lines = [match[0].strip().rstrip()]
    return lines

def get_target_lines(start, end, enc):
    lines = get_lines_with_sentence(start, end, enc)
    if not lines:
        # with lines "as is"
        lines = to_unicode(vim.current.buffer[start:end], enc)
    return map(_rest_caller.markup_paragraph_notranslate, lines)

_MAX_TARGET_RANGE = 100

def get_target_range():
    # take a range until next blank line if target range is not specified
    cur_row, cur_column = vim.current.window.cursor
    start = vim.current.range.start
    end = vim.current.range.end + 1
    if cur_row == end and (start + 1) == end:
        # it is considered as target range is not specified.
        _max_range = end + _MAX_TARGET_RANGE
        while vim.current.buffer[end:end + 1] != [""] and end < _max_range:
            end += 1
    return start, end

def translate_with_range(translator, enc):
    start, end = get_target_range()
    target_lines = get_target_lines(start, end, enc)
    # call translate API with multithread
    ret = _call_api_with_multithread(translator.translate, target_lines)
    api = ret[0][0]
    # previous and last empty lines are just for look and feel
    translated = ["", ] + [r.encode(enc) for _, r in ret] + ["", ]
    # add translated text into vim
    vim.current.buffer.append(translated, end)
    vim.command("let raimei_target_lines={0}".format(
                to_encode(target_lines, enc)))
    print "Translated by {0}".format(api.encode(enc))

def translate(api_name, lang_from, lang_to, enc):
    translator = _translate_api[api_name](lang_from, lang_to, None)
    return translate_with_range(translator, enc)

def comment_out_original_lines():
    start, end = get_target_range()
    start += 1
    vim.current.buffer.append("..", start - 1)
    for num, line in enumerate(vim.current.buffer[start:end + 1]):
        vim.current.buffer[start + num] = "{0}{1}".format(" " * 4, line)

def main():
    try:
        vim_vars = get_vim_variables()
        translate(*vim_vars)
        ext = splitext(vim.current.buffer.name)[1][1:]
        if ext == "rst":
            comment_out_original_lines()
    except Exception as err:
        print err.message
        return

if __name__ == "__main__":
    main()
