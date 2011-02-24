# -*- coding: utf-8 -*-
# Copyright: This module is put into the public domain.
# Author: Marcello Perathoner <webmaster@gutenberg.org>

"""

Mydocutils writer package.

"""

__docformat__ = 'reStructuredText'

import collections
import operator

from docutils import nodes, writers
import roman


class Writer (writers.Writer):
    """ A base class for writers. """

    output = None
    """Final translated form of `document`."""

    config_section_dependencies = ('writers',)

    def translate (self):
        visitor = self.translator_class (self.document)
        self.document.walkabout (visitor)
        self.output = visitor.astext ()

        
class TablePass1 (nodes.SparseNodeVisitor):

    """
    Makes a first pass over table to get row and col count.
    """
    
    def __init__ (self, document):
        nodes.SparseNodeVisitor.__init__ (self, document)
        
        self.row = -1     # 0-based
        self.column = 0   # 0-based
        self.cells = 0
        self.colspecs = None

    def visit_table (self, table):
        """ Called on each table. """
        self.colspecs = table.traverse (nodes.colspec)
        width = sum (map (operator.itemgetter ('colwidth'), self.colspecs))
        for colspec in self.colspecs:
            colspec['relative_width'] = float (colspec['colwidth']) / width

    def visit_row (self, dummy_node):
        """ Called on each table row. """
        self.row += 1
        self.column = 0
        for colspec in self.colspecs:
            colspec['spanned'] = max (0, colspec.get ('spanned', 0) - 1)
        
    def visit_entry (self, node):
        """ Called on each table cell. """

        morerows = node.get ('morerows', 0)
        morecols = node.get ('morecols', 0)

        self.cells += (morecols + 1) * (morerows + 1)

        # skip columns that are row-spanned by preceding entries
        while True:
            colspec = self.colspecs [self.column]
            if colspec.get ('spanned', 0) > 0:
                placeholder = nodes.entry ()
                placeholder['column'] = self.column
                placeholder.colspecs = self.colspecs[self.column:self.column + 1]
                placeholder['vspan'] = True
                node.replace_self ([placeholder, node])
                self.column += 1
            else:
                break

        # mark columns we row-span
        if morerows:
            for colspec in self.colspecs [self.column : self.column + 1 + morecols]:
                colspec['spanned'] = morerows + 1

        node['row'] = self.row
        node['column'] = self.column
        
        node.colspecs = self.colspecs[self.column:self.column + morecols + 1]

        self.column += 1 + morecols
        
        raise nodes.SkipNode

    def rows (self):
        """ Return the no. of columns. """
        return self.row + 1

    def cols (self):
        """ Return the no. of columns. """
        return self.cells / self.rows ()


class ListEnumerator:
    """ Enumerate according to type. """

    def __init__ (self, node, encoding):
        self.type  = node.get ('enumtype') or node.get ('bullet') or '*'
        self.start = node['start'] if 'start' in node else 1
        self.prefix = node.get ('prefix', '')
        self.suffix = node.get ('suffix', '')
        self.encoding = encoding

        self.indent = len (self.prefix + self.suffix) + 1
        if self.type == 'arabic':
            # indentation depends on end value
            self.indent += len (str (self.start + len (node.children)))
        elif self.type.endswith ('alpha'):
            self.indent += 1
        elif self.type.endswith ('roman'):
            self.indent += 5 # FIXME: calculate real length
        else:
            self.indent += 1 # bullets, etc.

    def get_next (self):
        """ Get next enumerator. """
        if self.type == '*':
            res = u'•' if self.encoding == 'utf-8' else '-'
        elif self.type == '-':
            res = u'-'
        elif self.type == '+':
            res = u'+'
        elif self.type == 'arabic':
            res = "%d" % self.start
        elif self.type == 'loweralpha':
            res = "%c" % (self.start + ord ('a') - 1)
        elif self.type == 'upperalpha':
            res = "%c" % (self.start + ord ('A') - 1)
        elif self.type == 'upperroman':
            res = roman.toRoman (self.start).upper ()
        elif self.type == 'lowerroman':
            res = roman.toRoman (self.start).lower ()
        else:
            res = "%d" % self.start

        self.start += 1

        return self.prefix + res + self.suffix

    def get_width (self):
        """ Get indent width for this list. """
        return self.indent


class Translator (nodes.NodeVisitor):
    """ nroff translator """

    admonitions = """
    attention caution danger error hint important note tip warning
    """.split ()

    docinfo_elements = """
    address author contact copyright date organization revision status
    version
    """.split ()

    inline_elements = """
    emphasis strong literal reference footnote_reference
    citation_reference substitution_reference title_reference
    abbreviation acronym subscript superscript inline problematic
    generated target image raw
    """.split ()

    body_elements = """
    paragraph compound container literal_block doctest_block
    line_block block_quote table figure image footnote citation rubric
    bullet_list enumerated_list definition_list field_list option_list
    attention caution danger error hint important note tip warning
    admonition reference target substitution_definition comment
    pending system_message raw
    """.split ()

    def __init__ (self, document):
        nodes.NodeVisitor.__init__ (self, document)
        self.settings = document.settings
        
        self.body = []
        self.context = self.body # start with context == body
        self.docinfo = collections.defaultdict (list)
        self.list_enumerator_stack = []
        self.section_level = 0
        self.vspace = 0 # pending space (need this for collapsing)

        self.last_output_type = None
        self.field_name = None
        self.compacting = 0 # > 0 if we are inside a compacting list
        
        self.inline_classes_prefixes = []  # order in which to apply classes
        self.inline_classes_suffixes = [] # reverse of above
        self.block_classes_prefixes = []  # order in which to apply classes
        self.block_classes_suffixes = [] # reverse of above
        
        self.environments = [] # holds pushed environments
        self.in_literal = 0 # are we inside one or more literal blocks?

        self.add_inline_handlers ('emphasis')
        self.add_inline_handlers ('strong')
        self.add_inline_handlers ('title_reference')
        self.add_inline_handlers ('literal')
        self.add_inline_handlers ('subscript',   'subscript')
        self.add_inline_handlers ('superscript', 'superscript')

        self.register_classes ()
        
        for name in self.docinfo_elements:
            setattr (self, 'visit_' + name,
                     lambda node: self.visit_field_body (node, name))
            setattr (self, 'depart_' + name, self.depart_field_body)
            
        for adm in self.admonitions:
            setattr (self, 'visit_' + adm,
                     lambda node: self.visit_admonition (node, adm))
            setattr (self, 'depart_' + adm, self.depart_admonition)
            
        self.attribution_formats = {'dash':         (u'———— ', ''),
                                    'parentheses':  ('(', ')'),
                                    'parens':       ('(', ')'),
                                    'none':         ('',  '')}

    def dispatch_visit (self, node):
        """
        Call self."``visit_`` + node class name" with `node` as
        parameter.  If the ``visit_...`` method does not exist, call
        self.unknown_visit.
        """
        node_name = node.__class__.__name__
        is_block = not isinstance (node, (nodes.Text, nodes.Inline))
        if is_block:
            self.pre_visit_block (node)
        method = getattr (self, 'visit_' + node_name, self.unknown_visit)
        self.document.reporter.debug (
            'docutils.nodes.NodeVisitor.dispatch_visit calling %s for %s'
            % (method.__name__, node_name))
        res =  method (node)
        if is_block:
            self.visit_block (node, [])
        return res

    def dispatch_departure (self, node):
        """
        Call self."``depart_`` + node class name" with `node` as
        parameter.  If the ``depart_...`` method does not exist, call
        self.unknown_departure.
        """
        node_name = node.__class__.__name__
        is_block = not isinstance (node, (nodes.Text, nodes.Inline))
        if is_block:
            self.depart_block (node, [])
        method = getattr (self, 'depart_' + node_name, self.unknown_departure)
        self.document.reporter.debug(
            'docutils.nodes.NodeVisitor.dispatch_departure calling %s for %s'
            % (method.__name__, node_name))
        res = method (node)
        if is_block:
            self.post_depart_block (node)
        return res

    def pre_visit_block (self, node):
        """ Called before visiting a block. """
        pass

    def post_depart_block (self, node):
        """ Called after visiting a block. """
        pass

    def visit_block (self, node, extra_classes):
        """ Called just inside a block, before visiting the inline elements. """
        pass

    def depart_block (self, node, extra_classes):
        """ Called at the end of a block, after visiting the inline elements. """
        pass

    def visit_inline (self, node, extra_classes = []):
        """ Visit an inline element. """
        pass

    def depart_inline (self, node, extra_classes = []):
        """ Depart from an inline element. """
        pass

    def add_inline_handlers (self, event, extra_classes = []):
        """ Helper. Add simple handlers events. """
        if isinstance (extra_classes, basestring):
            extra_classes = [extra_classes]
        setattr (self, 'visit_' + event,  lambda node: self.visit_inline  (node, extra_classes))
        setattr (self, 'depart_' + event, lambda node: self.depart_inline (node, extra_classes))

    def register_inline_class (self, class_, prefix, suffix):
        """ Register inline class. """
        self.inline_classes_prefixes.append ( (class_, prefix) )
        self.inline_classes_suffixes.insert (0, (class_, suffix))

    def register_block_class (self, class_, prefix, suffix):
        """ Register block class. """
        self.block_classes_prefixes.append ( (class_, prefix) )
        self.block_classes_suffixes.insert (0, (class_, suffix))

    def prefix_for_block (self, classes):
        return self.prefix_for_classes (classes, self.block_classes_prefixes)

    def suffix_for_block (self, classes):
        return self.prefix_for_classes (classes, self.block_classes_suffixes)

    def prefix_for_inline (self, classes):
        return self.prefix_for_classes (classes, self.inline_classes_prefixes)

    def suffix_for_inline (self, classes):
        return self.prefix_for_classes (classes, self.inline_classes_suffixes)

    def prefix_for_classes (self, classes, array):
        """ Helper for inline handlers. """
        res = ''
        if isinstance (classes, basestring):
            classes = classes.split ()
        for s in array:
            if s[0] in classes:
                res += s[1]
        return res
    
    def set_class_on_child (self, node, class_, index = 0):
        """
        Set class `class_` on the visible child no. index of `node`.
        Do nothing if node has fewer children than `index`.
        """
        children = [n for n in node if not isinstance (n, nodes.Invisible)]
        try:
            child = children[index]
        except IndexError:
            return
        child['classes'].append (class_)

    def set_first_last (self, node):
        """ Set class 'first' on first child, 'last' on last child. """
        self.set_class_on_child (node, 'first', 0)
        self.set_class_on_child (node, 'last', -1)
 	
    def astext (self):
        """ Return the final formatted document as a string. """
        return self.preamble () + ''.join (self.context) + self.postamble ()

    def text (self, text):
        """ Output text. """
        self.output_sp () # inline elements should never sp ()
        self.context.append (text)
        self.last_output_type = 'text'

    def sp (self, n = 1):
        """ Add vertical spacing. Delay output for collpasing. """
        if n == 0:
            self.vspace = 1999
        else:
            self.vspace = max (n, self.vspace)

    def output_sp (self):
        pass
    
    def push (self):
        """ Push environment. """
        pass
       
    def pop (self):
        """ Pop environment. """
        pass
        
    def up_if_last_line_shorter_than (self, length):
        """ Go one line up if the last line was shorter than length.

        Use this to compact lists etc. """
        pass
        
    def indent (self, by = 2):
        """ Indent text. """
        pass

    def rindent (self, by = 2):
        """ Indent text on the right side. """
        pass

    def preamble (self):
        return ''

    def postamble (self):
        return ''

    def visit_title (self, node):
        if isinstance (node.parent, nodes.section):
            self.visit_section_title (node)
        elif isinstance (node.parent, nodes.topic):
            self.visit_topic_title (node)
        elif isinstance (node.parent, nodes.table):
            self.visit_table_caption (node)
        elif isinstance (node.parent, nodes.document):
            self.visit_document_title (node)
        elif isinstance (node.parent, nodes.sidebar):
            pass
        elif isinstance (node.parent, nodes.admonition):
            pass
        else:
            assert ("Can't happen.")

    def depart_title (self, node):
        if isinstance (node.parent, nodes.section):
            self.depart_section_title (node)
        elif isinstance (node.parent, nodes.topic):
            self.depart_topic_title (node)
        elif isinstance (node.parent, nodes.table):
            self.depart_table_caption (node)
        elif isinstance (node.parent, nodes.document):
            self.depart_document_title (node)

    def visit_subtitle (self, node):
        if isinstance (node.parent, nodes.document):
            self.visit_document_subtitle (node)
        else:
            self.visit_section_subtitle (node)
        
    def depart_subtitle (self, node):
        if isinstance (node.parent, nodes.document):
            self.depart_document_subtitle (node)
        else:
            self.depart_section_subtitle (node)
        
