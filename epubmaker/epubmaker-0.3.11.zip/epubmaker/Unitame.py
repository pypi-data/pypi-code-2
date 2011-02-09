#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""
Unitame.py

Copyright 2010 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Module to implement the totally superfluous PG plain text conversion
into long extinct encodings.

We have to unitame-translate before feeding to nroff because nroff
does some irreversible (and wrong) translations of its own, like ä ->
a. Also, some unitame-translations change the number of characters,
thus throwing already-justified text off.

We cannot do the translations before feeding the source to docutils
because if we change the length of titles, we get the warning: Title
underline too short.

Translation does some dangerous things, like converting quotes to
apostrophes, which are command escapes in nroff. We have to escape
apostrophes in the source text but not apostroph-commands inserted by
the converter.

All this makes translation inside the docutils converter the best
choice. Implemented as a docutils translator that visits all text
nodes.

Smart quote translation should also go into a docutils
translator. Likewise a translator for text-transform: upper.

"""

import codecs
import unicodedata as ud

# UnitameData is generated from unitame.dat
from epubmaker.UnitameData import unicode_to_iso_8859_1, iso_8859_1_to_ascii

# tweak dicts for translate ()
u2i = dict ( [ (ord (o), s) for o, s in unicode_to_iso_8859_1.iteritems () ] )
i2a = dict ( [ (ord (o), s) for o, s in iso_8859_1_to_ascii.iteritems () ] )

u2i[ord (u'™')] = u'(tm)'

unhandled_chars = []

def strip_accents (text):
    """ Strip accents from string. """
    return ud.normalize ('NFKC', 
                         filter (lambda c: ud.category (c) != 'Mn', 
                                 ud.normalize ('NFKD', text)))


def unitame (exc):
    """
    Encoding error handler.

    On encoding error find a replacement for the character in the
    unitame database.

    """

    l = []
    for cc in exc.object[exc.start:exc.end]:
        c = cc
        if exc.encoding == 'latin-1': # python name for iso-8859-1
            c = c.translate (u2i)
            c = strip_accents (c)
            if ord (max (c)) < 256:
                l.append (c)
                c = None
        elif exc.encoding == 'ascii': # python name for us-ascii
            # 1¼ -> 1-1/4
            if cc in u'¼½¾':
                if exc.start > 0 and exc.object[exc.start - 1] in u'0123456789':
                    l.append ('-')
            c = c.translate (u2i)
            c = c.translate (i2a)
            c = strip_accents (c)
            if ord (max (c)) < 128:
                l.append (c)
                c = None

        if c is not None:
            l.append ('{~%s U+%04x~}' % (ud.name (cc), ord (cc)))
            unhandled_chars.extend (l)
        
    return (u"".join (l), exc.end)


codecs.register_error ('unitame', unitame)


