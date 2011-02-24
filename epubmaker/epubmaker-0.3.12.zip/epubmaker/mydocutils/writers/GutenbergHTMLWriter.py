#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""

GutenbergHTMLWriter.py

Copyright 2010 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

A modified HTML writer for PG.

"""

# FIXME: move hr.pb out of sections

import re

from docutils import nodes
from docutils.writers import html4css1

# from epubmaker.lib.Logger import info, debug, warn, error

from epubmaker.mydocutils.transforms import parts
from epubmaker.mydocutils import writers as mywriters

# in html attributes only nn and nn% are allowed
re_html_length = re.compile ('^[\d.]+%?$')

class Writer (html4css1.Writer):
    """ HTML Writer with PG tweaks. """
    
    def __init__ (self):
        html4css1.Writer.__init__ (self)
        self.translator_class = Translator

    ## def get_transforms (self):
    ##     tfs = html4css1.Writer.get_transforms (self)
    ##     return tfs + [parts.ImageWrapper]


class Translator (html4css1.HTMLTranslator):
    """ HTML Translator with PG tweaks. """
    
    html4css1.HTMLTranslator.attribution_formats['dash'] = (u'&mdash;&mdash; ', '')
                           
    def starttag (self, node, tagname, suffix='\n', empty=0, **attributes):
        """
        Tweak is: implement custom html attributes.

        Tweak is: original starttag produces side-effects on the node
        it operates on: ie. it changes the `classes` dict. Fix that.
        
        Construct and return a start tag given a node (id & class attributes
        are extracted), tag name, and optional attributes.

        """
        
        tagname = tagname.lower ()
        prefix = []
        atts = {}
        ids = []

        for (name, value) in attributes.items ():
            atts[name.lower()] = value
        if 'html_attributes' in node:
            atts.update (node['html_attributes'])

        classes = node.get ('classes', [])[:] # fix: make a copy
        
        if 'class' in atts:
            class_ = atts['class']
            if isinstance (class_, basestring):
                class_ = [class_]
            classes.extend (class_)
            del atts['class']

        styles = node.get ('styles', [])[:] # fix: make a copy

        if 'style' in atts:
            style = atts['style']
            if isinstance (style, basestring):
                style = [style]
            styles.extend (style)
            del atts['style']
        styles = [s.strip (' ;') for s in styles]

        assert 'id' not in atts
        ids.extend (node.get('ids', []))
        if 'ids' in atts:
            ids.extend (atts['ids'])
            del atts['ids']
        if ids:
            atts['id'] = ids[0]
            for id in ids[1:]:
                # Add empty "span" elements for additional IDs.  Note
                # that we cannot use empty "a" elements because there
                # may be targets inside of references, but nested "a"
                # elements aren't allowed in XHTML (even if they do
                # not all have a "href" attribute).
                if empty:
                    # Empty tag.  Insert target right in front of element.
                    prefix.append('<span id="%s"></span>' % id)
                else:
                    # Non-empty tag.  Place the auxiliary <span> tag
                    # *inside* the element, as the first child.
                    suffix += '<span id="%s"></span>' % id

        parts = []
        if classes:
            parts.append ('class="%s"' % ' '.join (sorted (set (classes))))
        if styles:
            parts.append ('style="%s"' % '; '.join (sorted (set (styles))))
        for name, value in sorted (atts.items ()):
            parts.append ('%s="%s"' % (name.lower (), value))

        infix = ' /' if empty else ''
        
        return ''.join(prefix) + '<%s %s%s>' % (tagname, u' '.join(parts), infix) + suffix


    def set_first_last (self, node):
        """ Set class 'first' on first child, 'last' on last child. """
        self.set_class_on_child (node, 'first', 0)
        self.set_class_on_child (node, 'last', -1)
 	

    ## def visit_title (self, node):
    ##     html4css1.HTMLTranslator.visit_title (self, node)
    ##     self.body.append ('<span class="strut"></span>')
        
    def visit_title (self, node):
        if isinstance (node.parent, nodes.table):
            self.body.append (self.starttag (node, 'caption'))
            if node.hasattr('refid'):
                atts = {
                    'class': 'toc-backref',
                    'href': '#' + node['refid'],
                    }
                self.body.append (self.starttag ({}, 'a', **atts))
                self.context.append ('</a></caption>\n')
            else:
                self.context.append ('</caption>\n')
        else:
            html4css1.HTMLTranslator.visit_title (self, node)

        
    def visit_subtitle (self, node):
        """ Tweak is: use <p> instead of <h?> """
        
        if isinstance (node.parent, (nodes.document, nodes.section, nodes.topic)):
            self.body.append (self.starttag (node, 'p'))
            self.context.append ('</p>\n')
            if isinstance (node.parent, nodes.document):
                self.in_document_title = len (self.body)
            return
        
        html4css1.HTMLTranslator.visit_subtitle (self, node)


    def visit_caption (self, node):
        """ Tweak is: use <div> instead of <p> """
        self.body.append (self.starttag (node, 'div', CLASS='caption'))
        
        atts = {}
        if node.hasattr ('refid'):
            atts['class'] = 'toc-backref'
            atts['href'] = '#' + node['refid']
            self.body.append (self.starttag ({}, 'a', **atts))


    def depart_caption (self, node):
        """ Tweak is: use <div> instead of <p> """
        if node.hasattr ('refid'):
            self.body.append ('</a>')
        self.body.append ('</div>\n')


    def visit_line (self, node):
        """ Tweak is: fix empty lines on ADE. """
        
        self.body.append (self.starttag (node, 'div', CLASS='line'))
        if not len (node):
            self.body.append (u' ') # U+00A0 nbsp


    def visit_line_block (self, node):
        """ Tweak is: noindent if centered or right-aligned. """
        
        if 'center' in node['classes']:
            node['classes'].append ('noindent')
        if 'right' in node['classes']:
            node['classes'].append ('noindent')
        self.body.append (self.starttag (node, 'div', CLASS='line-block'))


    def visit_table (self, node):
        pass_1 = mywriters.TablePass1 (self.document)
        node.walk (pass_1)
        
        options = { 'class': ['table'] }
        if 'align' in node:
            options['class'].append ('align-%s' % node['align'])
        if 'summary' in node:
            options['summary'] = node['summary']
        self.calc_centering_style (node)
        self.body.append (self.starttag (node, 'table', **options))


    def visit_thead (self, node):
        self.set_first_last (node)
        html4css1.HTMLTranslator.visit_thead (self, node)
        
    def visit_tbody (self, node):
        self.set_first_last (node)
        html4css1.HTMLTranslator.visit_tbody (self, node)
        
    def visit_entry (self, node):
        """ Tweak is: put alignment on element. """

        if 'vspan' in node:
            # HTML spans natively
            raise nodes.SkipNode

        node['styles'] = []
        align = node.colspecs[0].get ('align', 'left')
        if align != 'left':
            node['styles'].append ("text-align: %s" % align)
        valign = node.colspecs[0].get ('valign', 'middle')
        if valign != 'middle':
            node['styles'].append ("vertical-align: %s" % valign)
            
        html4css1.HTMLTranslator.visit_entry (self, node)

    def visit_target (self, node):
        if 'pageno' in node['classes']:
            options = { 'class': 'target' }
            # the ' ' avoids an empty span. firefox floats *all* text
            # following an empty span, instead of just the empty span.
            self.body.append (self.starttag (node, 'span', ' ', **options))
            self.context.append('</span>')
            return
        html4css1.HTMLTranslator.visit_target (self, node)


    def visit_page (self, node):
        if 'vspace' in node['classes']:
            node['styles'] = [ 'height: %dem' % node['length'] ]
        self.body.append (self.starttag (node, 'div'))

    def depart_page (self, node):
        self.body.append ('</div>\n')


    def visit_inline (self, node, extra_classes = []):
        options = {}
        if 'dropcap' in node['classes']:
            node['styles'] = [ "font-size: %.2fem" % (
                float (node.get ('lines', '2')) * 1.5) ]
        self.body.append (self.starttag (node, 'span', **options))


    def calc_centering_style (self, node):
        """
        Rationale: The EPUB standard allows user agents to replace
        `margin: auto` with `margin: 0`. Thus we cannot use `margin: auto`
        to center images, we have to calculate the left margin value.

        Also we must use 'width' on the html element, not css style,
        or Adobe ADE will not scale the image properly (ie. only
        horizontally).

        :align: is supposed to work on blocks. It floats or centers
        a block.

            `:align: center`
                Used on image: centers image
                Used on figure: centers image and caption
                Used on table: centers table and caption

        """

        width = node.get ('width')
        if width is None:
            return []
        
        style  = []

        style.append ('width: %s' % width)

        m = re.match ('(\d+)\s*%', width)
        if (m):
            width = max (min (int (m.group (1)), 100), 0)
            margin = 100 - width

            align = node.get ('align', 'center')
            if align == 'center':
                style.append ('margin-left: %d%%' % (margin / 2))
            if align == 'right':
                style.append ('margin-left: %d%%' % margin)
                
        node['styles'] = node.get ('styles', []) + style

    
    def visit_image (self, node):
        if 'dropcap' in node['classes']:
            node['height'] = "%.2fem" % (float (node.get ('lines', '2')) * 1.2)

        node['styles'] = []

        # check if we are a block image.
        # see class `TextElement` in `docutils.nodes`.
        if not isinstance (node.parent, nodes.TextElement):
            self.calc_centering_style (node)
            node['styles'].append ('display: block')
            
        if isinstance (node.parent, nodes.figure):
            if 'width' not in node:
                node['width'] = '100%'

        node['html_attributes'] = {}
        if 'width' in node and re_html_length.match (node['width']):
            node['html_attributes']['width'] = node['width']
        if 'height' in node and re_html_length.match (node['height']):
            node['html_attributes']['height'] = node['height']
        
        html4css1.HTMLTranslator.visit_image (self, node)


    def visit_figure (self, node):
        options = {}
        
        class_ = ['figure']
        if 'align' in node:
            class_.append ('align-' + node['align'])
        options['class'] = class_
        
        self.calc_centering_style (node)
            
        self.body.append (self.starttag (node, 'div', **options))

