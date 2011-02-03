# -*- coding: utf-8 -*-
# $Id: manpage.py 6270 2010-03-18 22:32:09Z milde $
# Author: Engelbert Gruber <grubert@users.sourceforge.net>
# Copyright: This module is put into the public domain.
# Rewritten almost completely
# by Marcello Perathoner <marcello@perathoner.de>

"""
Nroff writer for reStructuredText.

This is oriented towards authoring novel-type books, not
documentation.  Uses groff.

To process the output use:

  ``groff -t -K utf8 -T utf8 input > output``

"""

__docformat__ = 'reStructuredText'

from epubmaker.mydocutils.writers import NroffWriter

NROFF_PREAMBLE = r""".\" -*- mode: nroff -*- coding: {encoding} -*-
.\" This file produces Project Gutenberg plain text format:
.\"   $ groff -t -K {device} -T {device} this_file > output.txt
.
.pl 100000       \" very tall page: disable pagebreaks
.ll 72m
.po 0
.ad l           \" text-align: left
.nh             \" hyphenation: off
.cflags 0 .?!   \" single sentence space
.cflags 0 -\[hy]\[em]   \" don't break on -
.ev 0           \" start in a defined environment
.
"""

NROFF_POSTAMBLE = r""".
.pl 0    \" ends very long page here
.\" End of File
"""

class Writer (NroffWriter.Writer):
    """ A plaintext writer thru nroff. """

    supported = ('pg-nroff',)
    """Formats this writer supports."""

    def __init__ (self):
        NroffWriter.Writer.__init__ (self)
        self.translator_class = Translator

        
class Translator (NroffWriter.Translator):
    """ nroff translator """

    def __init__ (self, document):
        NroffWriter.Translator.__init__ (self, document)

    def register_classes (self):
        """ Register classes.
        
        Use the idiosyncratic PG convention of marking up italics etc.

        """
        
        self.register_inline_class ('italics',     r'_',    r'_')
        self.register_inline_class ('bold',        r'*',    r'*')
        self.register_inline_class ('monospaced',  r'',     r'')
        self.register_inline_class ('superscript', r'',     r'')
        self.register_inline_class ('subscript',   r'',     r'')

        self.register_inline_class ('small-caps',  r'_',    r'_')
        self.register_inline_class ('gesperrt',    r'_',    r'_')
        self.register_inline_class ('antiqua',     r'_',    r'_')
        self.register_inline_class ('larger',      r'',     r'')
        self.register_inline_class ('smaller',     r'',     r'')


        
    def preamble (self):
        return NROFF_PREAMBLE.format (encoding = self.encoding, device = self.device)

    def postamble (self):
        return NROFF_POSTAMBLE.format (encoding = self.encoding, device = self.device)

    def visit_section_title (self, node):
        """ Implements PG-standard spacing before headers. """
        self.sp (max (2, 5 - self.section_level))

    def visit_inline (self, node, extraclasses = []):
        if 'toc-pageref' in node['classes']:
            maxlen = self.document.max_len_page_number + 1
            self.cmd (('linetabs 1',
                       r'ta (\n[.l]u - \n[.i]u - %dm) +%dmR' % (maxlen, maxlen),
                       r'lc .'))
            self.text (chr (1) + '\t')
        NroffWriter.Translator.visit_inline (self, node, extraclasses)

    def visit_figure (self, node):
        self.sp (2)
        self.push ()

    def visit_image (self, node):
        # ignore alt attribute except for dropcaps
        if 'dropcap' in node['classes']:
            self.text (node.attributes.get ('alt', ''))

    def visit_caption (self, node):
        NroffWriter.Translator.visit_caption (self, node)
        self.cmd ('ad l')
        self.text ('[Illustration: ')

    def depart_caption (self, node):
        self.text (']')
        NroffWriter.Translator.depart_caption (self, node)


    def visit_page (self, node):
        if 'clearpage' in node['classes']:
            self.sp (4)
        elif 'cleardoublepage' in node['classes']:
            self.sp (4)
        else:
            NroffWriter.Translator.visit_page (self, node)

