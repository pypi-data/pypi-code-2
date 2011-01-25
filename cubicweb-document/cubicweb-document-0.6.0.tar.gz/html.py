"""minimalist html-in-python facility used by the docaster application

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
newspace = u'&#160;'

def tuplify(thing):
    if isinstance(thing, (list, tuple)):
        return thing
    return (thing,)

from cwtags.tag import (a, p, span, div, h1, h2, table, th, tr, td,
                        img, label, ul, li, option, legend, pre, form,
                        fieldset, input, select, textarea,
                        tag)

h4 = tag('h4')
thead = tag('thead')
tbody = tag('tbody')

def select_widget(w, choices, selected=None, **kwattrs):
    with select(w, **kwattrs):
        for value, label in choices:
            if value == selected:
                w(option(label, value=value, selected="selected"))
            else:
                w(option(label, value=value))
