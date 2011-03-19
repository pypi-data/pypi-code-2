"""
h2. Templated Tags

HTML tags with common usage pattern are pre-templated and can be used by
attaching the template name with HTML markup
''~[<''. And the text contained within '' ~[< .... >] '' are interpreted by
the template. For example, most of the pre-formatted text in this page are
generated using ''PRE'' template, like,
   > ~[<PRE preformatted text ~>]

   > [<PRE preformatted text >]
"""

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

import sys
import re

from   eazytext  import escape_htmlchars, split_style, obfuscatemail

def parsetag( text ) :
    html    = text
    keyword = text[:5].upper()
    if keyword[:3] == 'PRE' :
        html = tt_PRE( text[3:] )

    elif keyword[:4] == 'ABBR' :
        html = tt_ABBR( text[4:] )

    elif keyword[:4] == 'ADDR' :
        html = tt_ADDR( text[4:] )

    elif keyword[:3] == 'FNT' :
        html = tt_FNT( text[3:] )

    elif keyword[:5] == 'FIXME' :
        html = tt_FIXME()

    elif keyword[:1] == 'Q' :
        html = tt_Q( text[1:] )

    elif keyword[:3] == ':-)' :
        html = tt_SMILEYSMILE()

    elif keyword[:3] == ':-(' :
        html = tt_SMILEYSAD()

    elif keyword[:2] == 'FN' :
        html = tt_FOOTNOTE( text[2:] )

    return html


def tt_PRE( text ) :
    """
    |= Description | Generate preformated element |
    |= Syntax      | ~[<PRE //text// ~>]          |
    """
    template = '<span class="etttag pre">%s</span>'
    return  template % escape_htmlchars( text )

tt_PRE.example = '[<PRE sample text >]'


def tt_ABBR( text ) :
    """
    |= Description | Generate abbreviation element   |
    |= Syntax      | ~[<ABBR //text//, //title// ~>] |
    """
    args = text.split(',')
    cont = args and args.pop(0).strip() or ''
    title = args and args.pop(0).strip() or ''
    template = '<abbr class="etttag" title="%s">%s</abbr>'
    html =  template % ( title, cont )
    return html

tt_ABBR.example = '[<ABBR WTO, World Trade organisation >]'


def tt_FIXME() :
    """
    |= Description  | Generate FIXME label |
    |= Syntax       | ~[<FIXME~>]            |
    """
    template = '<span class="etttag fixme">%s</span>'
    html = template % 'FIXME'
    return html

tt_FIXME.example = '[<FIXME>]'

def tt_Q( text ) :
    """
    |= Description | Generate quotable quotes |
    |= Syntax      | ~[<Q -quote-text- ~>]    |

    html element generated is a div element with class attribute ''//qbq//''
    """
    template = '<div class="etttag qbq">%s</div>'
    html = template % text
    return html

tt_Q.example = """
[<Q
Emptying the heart of desires,
Filling the belly with food,
Weakening the ambitions,
Toughening the bones.
>]
"""

def tt_SMILEYSMILE() :
    """
    |= Description | Generate happy smiley Glyph |
    |= Syntax      | ~[<:-)~>]                   |
    """
    template = '<span class="etttag smile">%s</span>'
    html = template % '&#9786;'
    return html

tt_SMILEYSMILE.example = '[<:-)>] '


def tt_SMILEYSAD() :
    """
    |= Description | Generate sad smiley glyph |
    |= Syntax      | ~[<:-(~>]                  |
    """
    template = '<span class="etttag sad">%s</span>'
    html = template % '&#9785;'
    return html

tt_SMILEYSAD.example = '[<:-(>]'


def tt_ADDR( text ) :
    """
    |= Description | Generate `address` element              |
    |= Syntax      | ~[<ADDR //field1//, //field2//, ... ~>] |

    comma will be replaced with <br/> element
    """
    text = text.replace( ',', '<br/>' )
    template = '<address class="etttag">%s</address>'
    html = template % text
    return html

tt_ADDR.example = "[<ADDR 1, Presidency, St. Mark's Road, Bangalore-1 >]"


def tt_FNT( text ) :
    """
    |= Description | Generate a span element with specified font styling. |
    |= Syntax      | ~[<FNT <CSS font style> ; <text> ~>]                 |
    """
    try :
        style, innerHTML = text.split( ';', 1 )
    except :
        style = ''
        innerHTML = text
    template = '<span class="etttag fnt" style="font: %s">%s</span>'
    html = template % ( style, innerHTML )
    return html

tt_FNT.example = """
[<FNT italic bold 12px/30px Georgia, serif ;
This text is specially fonted >]
"""


def tt_FOOTNOTE( text ) :
    """
    |= Description | Generate footnote references. |
    |= Syntax      | ~[<FN text ~>] |

    Where `text` will be super-scripted and hyper-linked to foot-note content.

    """
    text = text.strip()
    template = '<sup class="etttag footnote">' + \
               '<a href="#%s" style="text-decoration: none;">%s' + \
               '</a></sup>'
    html = template % ( text, text )
    return html

tt_FOOTNOTE.example = """
... mentioned by Richard Feynman [<FN 1 >], initially proposed by
Albert Einstein  [<FN 2 >]

And foot-note content can be specified using the Wiki-extension language,
like,

{{{ Footnote //footnote-title//
1 German-born Swiss-American theoretical physicist, philosopher and
author who is widely regarded as one of the most influential and best
known scientists and intellectuals of all time. He is often regarded as
the father of modern physics.

2 American physicist known for his work in the path integral
formulation of quantum mechanics, the theory of quantum electrodynamics.
}}}
"""
