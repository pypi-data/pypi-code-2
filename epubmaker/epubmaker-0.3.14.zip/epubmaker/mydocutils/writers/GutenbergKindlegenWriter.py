#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""

GutenbergKindlegenWriter.py

Copyright 2011 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

A writer that writes input files suited for the Amazon Kindlegen utility.
N.B. This writer does not directly output the crippled Mobipocket HTML,
but a HTML that is suited best for conversion through Kindlegen.

Kindlegen does not understand multiple classes on one element, like
eg.  <div class='one two'>. In this case it misses both classes. To
fix this and other shortcomings of the Kindlegen CSS implementation we
use the class CSSApplicator later in the processing to move all CCS
from the CSS file onto the elements themselves.

Kindlegen does not differentiate between values of margin-left. All
values of margin-left > 0 yield exactly one blockquote.

A blockquote indents a fixed amount on the left side only. Nested
blockquotes increase the indentation on the left side until a maximum
indent is reached.

Kindlegen does not collapse vertical margins.


"""

# FIXME:
# ß put table caption outside of table
# ß space before page numbers in toc
# ß fix excessive footnote spacing (footnotes are tables)
# fix lists, compact list paragraphs

import re

from docutils import nodes

# from epubmaker.lib.Logger import info, debug, warn, error

from epubmaker.mydocutils.transforms import parts
from epubmaker.mydocutils import writers as mywriters
from epubmaker.mydocutils.writers.GutenbergHTMLWriter import Writer as WriterBase
from epubmaker.mydocutils.writers.GutenbergHTMLWriter import Translator as TranslatorBase


class Writer (WriterBase):
    """ Kindlegen writer. """
    
    def __init__ (self):
        WriterBase.__init__ (self)
        self.translator_class = Translator

    def get_transforms (self):
        tfs = WriterBase.get_transforms (self)
        return tfs + [parts.KindleTableCaption]


class Translator (TranslatorBase):
    """ HTML Translator with Kindle tweaks. """
    
    def compactable_paragraph_p (self, node):
        """
        Determine if the <p> tags around paragraph ``node`` can be omitted.
        """
        
        ## if not (self.compact_simple or self.compact_field_list):
        ##     return False
        
        if not isinstance (node.parent, (nodes.list_item, nodes.definition_list_item)):
            # Only compact paragraphs inside lists
            return False

        # Only the first paragraph can be compacted
        for child in node.parent.children:
            if isinstance (child, (nodes.label, nodes.Invisible)):
                continue
            if child is node:
                # I'm first, compact me
                return True
            # Something else came before me, don't compact
            return False
            
        return False # can't happen


    def visit_page (self, node):
        if 'vspace' in node['classes']:
            # Kindlegen knows no 'height' property
            node['styles'] = [ 'margin-top: %dem' % node['length'] ]
        self.body.append (self.starttag (node, 'div'))

        
    def visit_paragraph (self, node):
        if self.compactable_paragraph_p (node):
            self.body.append (self.starttag (node, 'span', CLASS='paragraph'))
            self.context.append ('</span>\n')
        else:
            # always use divs for Kindlegen, they are more predictable
            self.body.append (self.starttag (node, 'div', CLASS='paragraph'))
            self.context.append ('</div>\n')


    def visit_block_quote (self, node):
        self.body.append (self.starttag (node, 'div', CLASS='blockquote'))


    def depart_block_quote (self, node):
        self.body.append ('</div>\n')


    # Undo the markup changes in GutenbergHTMLWriter.
    #
    # In the Kindle format, if you jump into the middle of something
    # the renderer starts rendering at the exact point you jumped to
    # and doesn't give a damn about context, ie. that you are inside a
    # table.  So instead of having one table containing many
    # footnotes, here we use many tables containing one footnote.
    
    def visit_footnote_group (self, node):
        pass

    def depart_footnote_group (self, node):
        pass

    def visit_footnote (self, node):
        TranslatorBase.visit_footnote_group (self, node)
        self.body.append (self.starttag ({}, 'tr', CLASS='footnote'))
        self.footnote_backrefs (node)

    def depart_footnote (self, node):
        self.body.append ('</td></tr>\n')
        TranslatorBase.depart_footnote_group (self, node)


