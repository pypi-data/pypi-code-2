#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for Argot."""

import re

import lxml.html
import lxml.etree

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

def strip_surrounding_tag(text_or_element):
    """Strips the surrounding tag from text.  Useful when you primarily want
    to insert something into a container already existing within the page flow
    and don't want visual artifacts from the styling of the surrounding tag."""
    e = text_or_element
    if not isinstance(e, lxml.html.HtmlElement):
        try:
            e = lxml.html.fragment_fromstring(str(e))
        except lxml.etree.ParserError:
            return text_or_element
    s = lxml.etree.tostring(e)
    open_tag, close_tag = '<%s>' % (e.tag), '</%s>' % (e.tag)
    begin_pos = s.find(open_tag) + len(open_tag)
    end_pos = s.rfind(close_tag)
    return s[begin_pos:end_pos]

# code for this function taken from a snippet:
#   http://snippets.dzone.com/posts/show/4569
# original licensing applies
def decode_html_entities(string):
    """Decodes html entities like '&amp;' to '&' or '&lt;' to '<'."""
    def substitute_entity(match):
        from htmlentitydefs import name2codepoint as n2cp
        ent = match.group(2)
        if match.group(1) == "#":
            return unichr(int(ent))
        else:
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else:  return match.group()
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute_entity, string)[0]

fallback_text_lexer = get_lexer_by_name('text', stripnl=True, encoding='UTF-8')
def get_lexer(code, lang, fallback=fallback_text_lexer):
    """Gets a pygments lexer by language.  Falls back to the fallback."""
    if lang is None:
        try:
            lexer = guess_lexer(code)
        except ValueError:
            lexer = fallback_text_lexer
    else:
        try:
            lexer = get_lexer_by_name(lang, stripnl=True, encoding='UTF-8')
        except ValueError:
            lexer = fallback_text_lexer
    return lexer

def pygmentize(code, lang=None, cssclass='source'):
    """Highlight some code in language 'lang' using pygments.  The class name
    in `cssclass` is attributed to the resultant code div."""
    formatter = HtmlFormatter(cssclass=cssclass)
    lexer = get_lexer(code, lang)
    highlighted = highlight(code, lexer, formatter)
    return highlighted

