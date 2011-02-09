#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""

parts.py

Copyright 2010 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Slightly altered transformers for PG.

"""

import sys
import collections

from docutils import nodes
import docutils.transforms
import docutils.transforms.parts

import epubmaker.mydocutils.nodes as mynodes
from epubmaker.lib.Logger import error, info, debug, warn
from epubmaker import Unitame

# pylint: disable=W0142

class TocEntryTransform (docutils.transforms.Transform):
    """ Moves data of pending node onto next header. """

    default_priority = 719 # run before Contents Transform
    
    def apply (self, **kwargs):
        # debug ("TocEntryTransform %s" % repr (self.startnode.details))

        iter_ = self.startnode.traverse (nodes.section, ascend = 1, descend = 1)

        if len (iter_):
            section = iter_[0]
            title = section[0]
            # copy toc entry
            if 'toc_entry' in self.startnode.details:
                title['toc_entry'] = self.startnode.details['toc_entry']
                # debug ("Setting toc_entry: %s" % title['toc_entry'])
            else:
                title['toc_entry'] = None # suppress toc entry
            # copy depth
            if 'toc_depth' in self.startnode.details:
                section['toc_depth'] = self.startnode.details['toc_depth']
                # debug ("Setting toc_depth: %d" % section['toc_depth'])

        self.startnode.parent.remove (self.startnode)
            

class ContentsTransform (docutils.transforms.parts.Contents):
    """ A modified transform that obeys contents-depth directives. """

    def __init__ (self, document, startnode = None):
        docutils.transforms.parts.Contents.__init__ (self, document, startnode)
        self.depth = startnode.details.get ('depth', sys.maxint) if startnode else sys.maxint
        self.toc_depth = sys.maxint
        self.use_pagenos = 'page-numbers' in startnode.details

    def build_contents (self, node, level=0):
        # debug ('build_contents level %d' % level)
    
        entries = []
        for n in node:
            if isinstance (n, nodes.section):
                if 'toc_depth' in n:
                    self.toc_depth = n['toc_depth']
                    # debug ("New toc_depth: %d" % self.toc_depth)
                if level < self.depth and level < self.toc_depth:
                    subsects = self.build_contents(n, level + 1)
                    title = n[0]
                    # debug ('title: %s level: %d depth: %d' % (title, level, self.toc_depth))
                    auto = title.get ('auto')    # May be set by SectNum.

                    pagenos = []
                    if self.use_pagenos and 'pageno' in n:
                        inline = nodes.inline ('', n['pageno'])
                        inline['classes'].append ('toc-pageref')
                        pagenos.append (inline)
                    
                    if 'toc_entry' in  title:
                        text = title['toc_entry']
                        if not text: # suppress toc entry if emtpy
                            # debug ("Suppressing TOC entry")
                            continue
                        # debug ("Setting TOC entry to %s" % text)
                        text = nodes.Text (text)
                        entrytext = nodes.title ('', '', text)
                    else:
                        entrytext = self.copy_and_filter (title)
                        
                    reference = nodes.reference (
                        '', '', refid = n['ids'][0], *entrytext)
                    ref_id = self.document.set_id (reference)
                    entry = nodes.paragraph ('', '', reference, *pagenos)
                    item = nodes.list_item ('', entry)
                    item['classes'].append ('toc-entry')
                    if 'level' in title:
                        item['classes'].append ('level-%d' % (title['level']))
                    if (self.backlinks in ('entry', 'top')
                         and title.next_node (nodes.Referential) is None):
                        if self.backlinks == 'entry':
                            title['refid'] = ref_id
                        elif self.backlinks == 'top':
                            title['refid'] = self.toc_id
                    item += subsects
                    entries.append (item)
        if entries:
            contents = nodes.bullet_list ('', *entries)
            if auto:
                contents['classes'].append ('auto-toc')
            return contents
        else:
            return []


class FootnotesTransform (docutils.transforms.Transform):
    """
    Collects footnotes into this section.

    Moves all footnotes into this section in HTML format.
    Removes this section in other formats.
    
    """

    # run before contents transform. contents should not grab this
    # section's title because it can disappear.
    default_priority = 718
    
    def apply (self, **kwargs):
        pending = self.startnode
        section = pending.parent

        writer = self.document.transformer.components['writer']
        if writer.supports ('html'):
            debug ('FootnotesTransform')
        
            for footnote in self.document.traverse (nodes.footnote):
                footnote.parent.remove (footnote)
                section += footnote
            section.remove (pending)
        else:
            section.parent.remove (section)


class XetexFootnotesTransform (docutils.transforms.Transform):
    """
    Moves footnote body to reference.

    Inserts the footnote body immediately after the footnote reference
    in TeX format.
    
    """

    default_priority = 718
    
    def apply (self, **kwargs):
        # reversed () makes footnotes inside of footnotes come out in
        # the right order
        for footnote_reference in reversed (
            self.document.traverse (nodes.footnote_reference)):
            # pull in footnote body
            footnote = self.document.ids [footnote_reference['refid']]
            footnote_section = footnote.parent
            footnote_section.remove (footnote)
            
            parent = footnote_reference.parent
            index = parent.index (footnote_reference)
            parent.insert (index + 1, footnote)

            # if footnote is inside a table environment, move after
            # table
            while (parent):
                table = parent
                parent = parent.parent
                if isinstance (table, (nodes.table, nodes.title, nodes.footnote)):
                    footnote.parent.remove (footnote)
                    index = parent.index (table)
                    parent.insert (index + 1, footnote)
            
            # if footnote section became empty, remove
            iter_ = footnote_section.traverse (nodes.footnote, descend = 1)
            if len (iter_) == 0:
                footnote_section.parent.remove (footnote_section)

        
class PageNumberMoverTransform (docutils.transforms.Transform):
    """ Moves paragraphs that contain only page numbers into next paragraph. """

    default_priority = 721 # after contents transform
    
    def apply (self, **kwargs):
        for target in self.document.traverse (nodes.target):
            if (isinstance (target.parent, nodes.paragraph) and len (target.parent) == 1):
                # move onto next appropriate node
                for next_node in target.traverse (nodes.TextElement, include_self = 0, ascend = 1):
                    if (not isinstance (next_node, (nodes.Structural, nodes.Special))):
                        target.parent.parent.remove (target.parent)
                        next_node.insert (0, target)
                        break
            
                    
class TocPageNumberTransform (docutils.transforms.Transform):
    """ Finds the page number all sections are in. """

    default_priority = 719 # before contents transform
    
    def __init__ (self, document, startnode = None):
        docutils.transforms.Transform.__init__ (self, document, startnode)
        self.pageno = '' # pageno is actually a string
        self.maxlen = 0  # longest pagenumber

    def apply (self, **kwargs):
        for n in self.document.traverse ():
            if isinstance (n, nodes.target) and 'pageno' in n['classes']:
                self.pageno = n['html_attributes']['title']
                self.maxlen = max (self.maxlen, len (self.pageno))
                continue
            if isinstance (n, nodes.section):
                n['pageno'] = self.pageno
                continue
        self.document.max_len_page_number = self.maxlen


class TabularColumnsTransform (docutils.transforms.Transform):
    """

    Move the 'colspec' attribute specified in the `pending` node to the
    immediately following table element.
    
    """

    default_priority = 210

    def apply (self):
        pending = self.startnode
        iter_ = pending.traverse (nodes.table, siblings = 1)

        if len (iter_):
            table = iter_[0]
            table['colspec'] = pending.details['colspec']
            pending.parent.remove (pending)
        else:
            error = self.document.reporter.error (
                'No suitable element following "%s" directive'
                % pending.details['directive'],
                nodes.literal_block (pending.rawsource, pending.rawsource),
                line = pending.line)
            pending.replace_self (error)


class DropCapTransform (docutils.transforms.Transform):
    """ Inserts a dropcap into the next paragraph. """

    default_priority = 719 # run before Contents Transform
    
    def apply (self, **kwargs):
        iter_ = self.startnode.traverse (nodes.paragraph, siblings = 1)

        if len (iter_):
            para = iter_[0]
            iter_ = para.traverse (nodes.Text)
            details = self.startnode.details

            if len (iter_):
                textnode = iter_[0]
                charnode = spannode = restnode = None

                char = details['char']
                if not textnode.startswith (char):
                    error ("Dropcap: next paragraph doesn't start with: '%s'." % char)
                    return

                span = details.get ('span', '')
                if not textnode.startswith (span):
                    error ("Dropcap: next paragraph doesn't start with: '%s'." % span)
                    return
                if span and not span.startswith (char):
                    error ("Dropcap: span doesn't start with: '%s'." % char)
                    return
                if span == char:
                    span = ''

                if span:
                    # split into char/span/rest
                    restnode = nodes.Text (textnode.astext ()[len (span):])
                    spannode = nodes.inline ()
                    spannode.append (nodes.Text (textnode.astext ()[len (char):len (span)]))
                    spannode['classes'].append ('dropspan')
                else:
                    # split into char/rest
                    restnode = nodes.Text (textnode.astext ()[len (char):])
                    spannode = nodes.Text ('')
                
                if 'image' in details:
                    charnode = nodes.image ()
                    charnode['uri'] = details['image']
                    charnode['alt'] = char
                    # debug ("Inserting image %s as dropcap." % uri)
                else:
                    charnode = nodes.inline ()
                    charnode.append (nodes.Text (char))
                    # debug ("Inserting char %s as dropcap." % char)

                charnode['classes'].append ('dropcap')
                charnode.attributes.update (details)

                para.replace (textnode, [charnode, spannode, restnode])

        self.startnode.parent.remove (self.startnode)


class CharsetTransform (docutils.transforms.Transform):
    """
    Translates text into smaller charset.

    This does not encode, just replaces the characters of the larger
    charset that are not in the smaller charset.

    """

    default_priority = 899 # last
    
    def apply (self, **kwargs):
        if self.document.settings.encoding != 'utf-8':
            charset = self.document.settings.encoding
            del Unitame.unhandled_chars[:]

            for n in self.document.traverse (nodes.Text):
                text = n.astext ().encode (charset, 'unitame').decode (charset)
                n.parent.replace (n, nodes.Text (text)) # cannot change text nodes

            if Unitame.unhandled_chars:
                error ("unitame: unhandled chars: %s" % u", ".join (set (Unitame.unhandled_chars)))
            

class StyleTransform (docutils.transforms.Transform):
    """
    Add classes to elements.

    Works in a way similar to CSS, though you can select only on
    element and class.

    Works on all following elements in the section it is used, if used
    before the first section works on the rest of the document.
    
    """

    default_priority = 730 # after contents
    
    def apply (self, **kwargs):
        pending  = self.startnode
        selector  = pending.details.get ('selector', '')

        if '.' not in selector:
            selector += '.'
            
        match_element, match_classes = selector.split ('.', 1)
        match_classes = set (match_classes.split ('.')) if match_classes else set ()

        classes   = pending.details.get ('class', [])
        rmclasses = pending.details.get ('rmclass', [])
        language  = pending.details.get ('language', '')
        
        if match_element == 'document':
            # look at document node only
            node_list = [self.document]
        else:
            # traverse all following nodes and their children
            node_list = pending.traverse (nodes.Element, siblings = 1, include_self = 0)
            
        for n in node_list:
            #if isinstance (n, nodes.pending):
            #    # next directive with same selector ends scope
            #    if n.details.get ('selector', '') == pending.details.get ('selector', ''):
            #        break
            #    continue

            element = n.__class__.__name__
            
            #print 'element: ', element, n['classes']
            
            if match_element and (match_element != element):
                continue

            if match_classes.issubset (n['classes']):
                # print 'matched: ', match_element, match_classes
                n['classes'] = list ((set (n['classes']) | set (classes)) - set (rmclasses))
                if language:
                    n['html_attributes'] = {'xml:lang': language }
                
        pending.parent.remove (pending)
        

class DefaultPresentation (docutils.transforms.Transform):
    """
    Set a default class on nodes with no classes.

    """
    
    default_priority = 800 # late

    default_presentation = {
        'emphasis':        'italics',
        'strong':          'bold',
        'title_reference': 'italics',
        'literal':         'monospaced',
        'caption':         'italics',
        # 'reference':       '',
        #'subscript':       'subscript',
        #'superscript':     'superscript',
        }

    def apply (self):
        for node in self.document.traverse ():
            name = node.__class__.__name__
            if name in self.default_presentation:
                if not node['classes']:
                    node['classes'] = [ self.default_presentation[name] ]


class AlignTransform (docutils.transforms.Transform):
    """
    Transforms align attribute into align-* class.

    """
    
    default_priority = 801 # late

    def apply (self):
        for body in self.document.traverse (nodes.Body):
            if 'align' in body:
                body['classes'].append ('align-%s' % body['align'])


class TextTransform (docutils.transforms.Transform):
    """
    Implements CSS text-transform.

    FIXME: what if we need uppercase AND smartquotes?

    """

    default_priority = 898 # next to last

    smartquotes_map = {
        0x0027: u'’',
        # 0x0022: u'”',
        }
    
    def apply (self, **kwargs):
        self.recurse (self.document, 'none')

    def recurse (self, node, text_transform):
        if isinstance (node, nodes.Text):
            if text_transform == 'none':
                return
            if text_transform == 'uppercase':
                text = node.astext ().upper ()
                node.parent.replace (node, nodes.Text (text)) # cannot change text nodes
            elif text_transform == 'smartquotes':
                text = node.astext ().translate (self.smartquotes_map)
                node.parent.replace (node, nodes.Text (text)) # cannot change text nodes
            return

        ntt = text_transform
        classes = node['classes']
        
        if 'text-transform-uppercase' in classes:
            ntt = 'uppercase'
        elif 'text-transform-smartquotes' in classes:
            ntt = 'smartquotes'
        elif 'text-transform-none' in classes:
            ntt = 'none'
            
        for child in node:
            self.recurse (child, ntt)


class TitleLevelTransform (docutils.transforms.Transform):
    """
    Adds some useful classes to sections and titles.

    Add `level-N` to `section`, `title` and `subtitle` nodes.

    Add `document-title` or `section-title`.

    Add `title` or `subtitle`.

    Add `with-subtitle`.

    """
    
    default_priority = 360 # after title promotion

    def apply (self, **kwargs):
        self.recurse (self.document, 1)

    def recurse (self, parent, level):
        for node in parent:
            if isinstance (node, nodes.Text):
                continue

            if isinstance (node, (nodes.title, nodes.subtitle)):
                nclass  = node.__class__.__name__
                pclass  = parent.__class__.__name__
                classes = [nclass,
                           '%s-%s' % (pclass, nclass),
                           'level-%d' % level]
                if (isinstance (node, (nodes.title)) and
                    len (parent) >= 2 and
                    isinstance (parent[1], nodes.subtitle)):
                    classes.append ('with-subtitle')
                node['classes'].extend (classes)
                node['level'] = level
            
            if isinstance (node, nodes.section):
                node['classes'].append ('level-%d' % (level + 1))
                node['level'] = level + 1

                self.recurse (node, level + 1)
            else:
                self.recurse (node, level)


class FirstParagraphTransform (docutils.transforms.Transform):
    """
    Mark first paragraphs.

    With indented paragraphs, the first paragraph following a
    vertical space should not be indented. This transform tries
    to figure out which paragraphs should not be indented.
    
    Add the classes `pfirst` and `pnext` to paragraphs.

    """
    
    default_priority = 361 # after title promotion

    def apply (self, **kwargs):
        self.recurse (self.document)

    def recurse (self, parent):
        follows_paragraph = False # flag: previous element is paragraph
        
        for node in parent:
            
            if isinstance (node, nodes.paragraph):
                node['classes'].append ('pnext' if follows_paragraph else 'pfirst')
                follows_paragraph = True
            elif isinstance (node, (nodes.title, nodes.subtitle)):
                # title may also be output as <html:p>
                node['classes'].append ('pfirst')
                follows_paragraph = False
            elif isinstance (node, (nodes.Invisible, nodes.footnote)):
                # invisible nodes are neutral, footnotes are pulled away
                pass
            else:
                follows_paragraph = False

            if not isinstance (node, nodes.Text):
                self.recurse (node)


class XetexMetaCollector (docutils.transforms.Transform):
    """
    Collects meta nodes for Xetex.

    In an ill-advised effort to clean up, the `Filter` transform
    throws out all `pending` nodes with meta information if the writer
    format is not HTML. But PDF can have metadata too. We grab the
    metadata and store them in ``document.meta_block``.

    """
    
    default_priority = 779 # before Filter transform

    def apply (self):
        self.document.meta_block = collections.defaultdict (list)
        
        for pending in self.document.traverse (nodes.pending):
            try:
                meta = pending.details['nodes'][0]
                name = meta.attributes['name']
                content = meta.attributes['content']
                self.document.meta_block[name].append (content)
            except:
                pass



class ImageWrapper (docutils.transforms.Transform):
    """
    Wrap a block-level image into a figure.

    """
    
    default_priority = 800 # late

    def apply (self):
        for image in self.document.traverse (nodes.image):
            # check if we are a block image.
            # see class `TextElement` in `docutils.nodes`.
            if not isinstance (image.parent, (nodes.TextElement, nodes.figure)):
                figure = nodes.figure ()
                for clas in ('align', 'width'):
                    if clas in image:
                        figure[clas] = image[clas]
                image['width'] = '100%'
                if 'align' in image:
                    del image['align']
                image.replace_self (figure)
                #image.parent.insert (image.parent.index (image), figure)
                #image.parent.remove (image)
                figure.append (image)
                

class Lineblock2VSpace (docutils.transforms.Transform):
    """
    Turn empty line_blocks into page nodes.

    """
    
    default_priority = 200 # early, before vspace

    def apply (self):
        for lb in self.document.traverse (nodes.line_block):
            if lb.astext ().strip () == '':
                gap_len = len (lb)
                page = mynodes.page ()
                page['classes'].append ('vspace')
                page['length'] = gap_len
                lb.replace_self (page)
