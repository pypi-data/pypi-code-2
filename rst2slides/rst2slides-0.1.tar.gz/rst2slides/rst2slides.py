#!/usr/bin/env python

# Author: Bruno Renie <bruno@renie.fr>
# Based on the HTML5 slides by Googlers:
#   Copyright 2010 Google Inc.
#   All rights reserved.
#   Original slides: Marcin Wichary (mwichary@google.com)
#   Modifications: Ernest Delgado (ernestd@google.com)

"""
HTML5 Slideshow Writer
"""

__docformat__ = 'reStructuredText'


import os
import re
import sys
import shutil
import docutils
from docutils import frontend, nodes, utils, languages
from docutils.writers import html4css1
from docutils.parsers.rst import directives
from docutils._compat import b

from . import __version__, url


class Writer(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTML5Translator

class HTML5Translator(html4css1.HTMLTranslator):
    doctype = '<!DOCTYPE html>\n'
    head_prefix_template = '<html lang="%s">\n'
    content_type = '<meta charset="%s">\n'
    stylesheet_link = '<link rel="stylesheet" href="ui/styles.css" />\n'\
                      '<link rel="stylesheet" href="ui/fonts.css" />\n'
    nav = """\n
    <header>
    <nav>
        <ul>
            <li><button id="prev-btn" title="Previous slide">Previous Slide</button></li>
            <li><span id="slide-number"></span>/<span id="slide-total"></span></li>
            <li><button id="next-btn" title="Next Slide">Next Slide</button></li>
        </ul>
    </nav>
    </header>\n"""
    js = """\n
        <script src="ui/jquery-1.4.2.min.js"></script>
        <script src="ui/htmlSlides.js"></script>
        """
    generator = '<meta name="generator" content="rst2slides %s " />'


    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode)
        self.meta = [self.content_type % settings.output_encoding,
                     self.generator % __version__]
        self.head_prefix = []
        self.html_prolog = []
        #if settings.xml_declaration:
        #    self.head_prefix.append(self.xml_declaration
        #                            % settings.output_encoding)
            # encoding not interpolated:
            #self.html_prolog.append(self.xml_declaration)
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template % lcode])
        self.html_prolog.append(self.doctype)
        self.head = self.meta[:]
        # stylesheets
        styles = utils.get_stylesheet_list(settings)
        if settings.stylesheet_path and not(settings.embed_stylesheet):
            styles = [utils.relative_path(settings._destination, sheet)
                      for sheet in styles]
        self.stylesheet = [self.stylesheet_link,]
        self.body_prefix = ['</head>\n<body>%s\n' % self.nav]
        # document title, subtitle display
        self.body_pre_docinfo = []
        # author, date, etc.
        self.docinfo = []
        self.body = []
        self.fragment = []
        self.body_suffix = ['%s</body>\n</html>\n' % self.js]
        self.section_level = 0
        self.initial_header_level = int(settings.initial_header_level)
        # A heterogenous stack used in conjunction with the tree traversal.
        # Make sure that the pops correspond to the pushes:
        self.context = []
        self.topic_classes = []
        self.colspecs = []
        self.compact_p = 1
        self.compact_simple = None
        self.compact_field_list = None
        self.in_docinfo = None
        self.in_sidebar = None
        self.title = []
        self.subtitle = []
        self.header = []
        self.footer = []
        self.html_head = [self.content_type] # charset not interpolated
        self.html_title = []
        self.html_subtitle = []
        self.html_body = []
        self.in_document_title = 0
        self.in_mailto = 0
        self.author_in_authors = None
        self.quit_next = False
    


    def depart_document(self, node):
        self.fragment.extend(self.body)
        self.body_prefix.append("<div id='deck'>\n")
        self.body_suffix.insert(0, '</div>\n')
        self.html_head.extend(self.head[1:])
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])
        self.copy_files()

    def visit_section(self, node):
        if self.quit_next:
            self.body.append('</section>\n')
            self.quit_next = False
        self.section_level += 1
        if self.section_level == 1:
            self.body.append('<section>\n')

    def depart_section(self, node):
        self.section_level -= 1
        if self.section_level == 0:
            self.body.append('  </section>\n\n')

    def visit_title(self, node):
        if self.section_level == 0:
            self.body.append('<section>\n')
            self.quit_next = True
        if self.section_level in (0, 1):
            self.body.append('<hgroup>\n')
            self.body.append('    <h1>\n')
        else:
            self.body.append('    <h%s>\n' % self.section_level)

    def depart_title(self, node):
        if self.section_level in (0, 1):
            self.body.append('    </h1>\n')
            self.body.append('</hgroup>\n')
        else:
            self.body.append('    </h%s>\n' % self.section_level)


    def copy_files(self):
        """
        Locate & copy js and css.
        """

        orig_path = os.path.join(os.path.dirname(__file__), 'data', 'ui')
        orig_path = os.path.abspath(orig_path)
        dest_path = os.path.join(os.getcwd(), 'ui')

        try:
            shutil.copytree(orig_path, dest_path)
        except OSError:
            print './ui exists. Not copied.'
            raise

