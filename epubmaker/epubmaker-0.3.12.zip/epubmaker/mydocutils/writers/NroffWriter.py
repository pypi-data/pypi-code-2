# -*- coding: utf-8 -*-
# Copyright: This module is put into the public domain.
# Author: Marcello Perathoner <webmaster@gutenberg.org>

"""
Nroff writer for reStructuredText.

This module is more suitable for writing novel-type books than
documentation.

To process into plain text use:

  ``groff -t -K utf8 -T utf8 input.nroff > output.txt``

"""

__docformat__ = 'reStructuredText'

import collections
import re

from docutils import nodes, frontend
from docutils.writers.html4css1 import SimpleListChecker

from epubmaker.mydocutils import writers

LINE_WIDTH             = 66
TABLE_WIDTH            = 66 # max. table width

BLOCKQUOTE_INDENT      =  4
LIST_INDENT            =  2
FOOTNOTE_INDENT        =  5
CITATION_INDENT        = 10
FIELDLIST_INDENT       =  7
DEFINITION_LIST_INDENT =  7
OPTION_LIST_INDENT     =  7

NROFF_PREAMBLE = r""".
.ad l           \" text-align: left
.ev 0           \" start in a defined environment
.
"""

NROFF_POSTAMBLE = r""".
.\" Local Variables:
.\" mode: nroff
.\" encoding: utf-8
.\" End:
"""

def nroff_units (length_str, reference_length = None):
    """ Convert rst units to Nroff units. """

    match = re.match ('(\d*\.?\d*)\s*(\S*)', length_str)
    if not match:
        return length_str

    value, unit = match.groups ()

    if unit in ('', 'u'):
        return value

    # percentage: relate to current line width
    elif unit == '%':
        reference_length = reference_length or LINE_WIDTH
        return int (float (value) / 100.0 * reference_length)

    return length_str

class Writer (writers.Writer):
    """ A plaintext writer thru nroff. """

    supported = ('nroff',)
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    settings_spec = (
        'Nroff-Specific Options',
        None,
        (('Should lists be compacted when possible?',
          ['--compact-lists'],
          {'default': 1,
           'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Format for block quote attributions: one of "dash" (em-dash '
          'prefix), "parentheses"/"parens", or "none".  Default is "dash".',
          ['--attribution'],
          {'choices': ['dash', 'parentheses', 'parens', 'none'],
           'default': 'dash', 'metavar': '<format>'}),
         ('Which encoding are we targeting? (As hint to the writer.).',
          ['--encoding'],
          {'default': 'utf-8',
           'validator': frontend.validate_encoding}),))

    settings_defaults = {'encoding': 'utf-8'}

    config_section = 'NROFF writer'
    
    config_section_dependencies = ('writers',)

    def __init__ (self):
        writers.Writer.__init__ (self)
        self.translator_class = Translator

    def translate (self):
        visitor = self.translator_class (self.document)
        self.document.walkabout (visitor)
        self.output = visitor.astext ()

        
class TablePass2 (nodes.SparseNodeVisitor):

    """
    Makes a second pass over table to build tbl format specification.
    """
    
    def __init__ (self, document, table, rows, cols):
        nodes.SparseNodeVisitor.__init__ (self, document)
        self.cols = cols
        self.types = ['-'] * (rows * cols)
        self.i = 0

        self.table_width = nroff_units (table.get ('width', '100%'), TABLE_WIDTH)
        colspecs = table.traverse (nodes.colspec)
        self.table_width -= len (colspecs) * 2

    def visit_entry (self, node):
        """ Called on each table cell. """

        if 'vspan' in node:
            raise nodes.SkipNode

        rows = node.get ('morerows', 0) + 1
        cols = node.get ('morecols', 0) + 1
        
        for j in range (0, cols):
            self.types[self.i + j] = 's'
            for k in range (1, rows):
                self.types[self.i + (k * self.cols) + j] = '^'

        align = node.colspecs[0].get ('align', 'left')
        align = { 'right': 'r', 'center': 'c' }.get (align, 'l')
        self.types[self.i] = align # l, r or c

        valign = node.colspecs[0].get ('valign', 'middle')
        valign = { 'top': 't', 'bottom': 'd' }.get (valign, '')
        self.types[self.i] += valign # t or d
        
        if len (node.colspecs) == 1: # no span
            self.types[self.i] += 'w(%d)' % (
                node.colspecs[0]['relative_width'] * self.table_width)
        
        while self.i < len (self.types) and self.types[self.i] != '-':
            self.i += 1
                        
        raise nodes.SkipNode

    def build_format_spec (self):
        """ Build a tbl format specification for this table. """
        types = zip (*[iter (self.types)] * self.cols) # cluster by row
        
        types = map (lambda x: ' '.join (x), types)
        types = ','.join (types)

        # print types
        
        return '%s.\n' % types


class Translator (writers.Translator):
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

    superscript_digits = u'⁰¹²³⁴⁵⁶⁷⁸⁹'
    
    subscript_digits   = u'₀₁₂₃₄₅₆₇₈₉'

    def __init__ (self, document):
        writers.Translator.__init__ (self, document)
        self.settings = document.settings
        
        self.encoding = self.settings.encoding
        self.device = { 'utf-8': 'utf8',
                        'iso-8859-1': 'latin1',
                        'us-ascii': 'ascii' }.get (self.encoding, '<device>')
        self.body = []
        self.context = self.body # start with context == body
        self.docinfo = collections.defaultdict (list)
        self.list_enumerator_stack = []
        self.section_level = 0
        self.vspace = 0 # pending space (need this for collapsing)
        self.pending = [] # pending stuff (currently not used)
        self.last_output_type = None
        self.field_name = None
        self.compacting = 0 # > 0 if we are inside a compacting list
        self.env_depth = 0 # no. of pushed environments
        self.in_literal = 0 # are we inside one or more literal blocks?

        self.attribution_formats = {'dash': (u'———— ' if self.encoding == 'utf-8' else '---- ', ''),
                                    'parentheses': ('(', ')'),
                                    'parens': ('(', ')'),
                                    'none': ('', '')}

    def register_classes (self):
        """ Register classes.

        Use a fairly general set of font attributes.
        
        """
        
        self.register_inline_class ('align-left',   '\n.ad l\n',  '')
        self.register_inline_class ('align-right',  '\n.ad r\n',  '')
        self.register_inline_class ('align-center', '\n.ad c\n',  '')
        
        self.register_inline_class ('left',         '\n.ad l\n',  '')
        self.register_inline_class ('right',        '\n.ad r\n',  '')
        self.register_inline_class ('center',       '\n.ad c\n',  '')
                                                    
        self.register_inline_class ('italics',     r'\fI',    r'\fP')
        self.register_inline_class ('bold',        r'\fB',    r'\fP')
        self.register_inline_class ('monospaced',  r'\fM',    r'\fP')
        self.register_inline_class ('superscript', r'\s-2\u', r'\d\s0')
        self.register_inline_class ('subscript',   r'\s-2\d', r'\u\s0')
        
        self.register_inline_class ('small-caps',  r'\fI',    r'\fP')
        self.register_inline_class ('gesperrt',    r'\fI',    r'\fP')
        self.register_inline_class ('antiqua',     r'\fI',    r'\fP')
        self.register_inline_class ('larger',      r'\fI',    r'\fP')
        self.register_inline_class ('smaller',     r'\fI',    r'\fP')


    def preamble (self):
        """ Inserts nroff preamble. To override. """
        return NROFF_PREAMBLE

    def postamble (self):
        """ Inserts nroff postamble. To override. """
        return NROFF_POSTAMBLE

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
 	
    def cmd (self, cmds):
        """ Add nroff commands. """
        if isinstance (cmds, basestring):
            cmds = [cmds]

        if self.last_output_type == 'text':
            self.context.append ('\n')
        for c in cmds:
            self.context.append (".%s\n" % c)
        self.last_output_type = 'cmd'
        
    def output_sp (self):
        """ Output spacing and pending stuff. """
        if self.vspace == 1999: # magic number to eat all space
            self.vspace = 0
        if self.vspace:
            self.cmd ('sp' if self.vspace == 1 else 'sp %d' % self.vspace)
            self.vspace = 0
        if self.pending:
            self.context.extend (self.pending)
            self.pending = []

    def text (self, text):
        """ Output text. """
        if text:
            self.output_sp () # inline elements should never sp ()
            self.context.append (text)
            self.last_output_type = 'text'

    def comment (self, text):
        """ Output nroff comment. """
        self.context.append ('.\\"%s\n' % text)
        self.last_output_type = 'cmd'

    def sp (self, n = 1):
        """ Add vertical spacing. Delay output for collpasing. """
        if n == 0:
            self.vspace = 1999
        else:
            self.vspace = max (n, self.vspace)

    def br (self):
        """ Insert br command. """
        self.cmd ('br')

    def ta (self, indent, text):
        """ Tabulate text to indent position. """
        self.cmd ('ta %dmR' % indent)
        self.text ('\t' + text)
        
    def push (self):
        """ Push environment. """
        self.env_depth += 1
        self.br ()
        self.cmd ('ev %d' % self.env_depth)
        self.cmd ('evc %d' % (self.env_depth - 1))
        
    def pop (self):
        """ Pop environment. """
        self.br ()
        self.cmd ('ev')
        self.env_depth -= 1
        
    def as_superscript (self, n):
        """ Return n as string using superscript unicode chars. """
        if self.encoding != 'utf-8':
            return '[%d]' % n
        res = ''
        for d in str (n):
            res += self.superscript_digits [int (d)]
        return res

    def up_if_last_line_shorter_than (self, length):
        """ Go one line up if the last line was shorter than length.

        Use this to compact lists etc. """
        self.br ()
        self.cmd (r'if (\n[.n] < %dm) .sp -1' % length)
        
    def indent (self, by = 2):
        """ Indent text. """
        self.cmd ('in +%dm' % by)

    def rindent (self, by = 2):
        """ Indent text on the right side. """
        self.cmd ('ll -%dm' % by)

    # pylint: disable=C0111
    # pylint: disable=W0613

    re_command_dot  = re.compile (r'^\.', re.M)
    re_command_apos = re.compile (r"^'", re.M)

    # see: man groff_char
    translate_map = translate_map_literal = {
        0x005c: ur"\N'92'",  # groff escape char
        0x00a0: ur'\~',      # groff doesn't know nbsp. strange.
        0x2009: ur'',        # remove thin space 
    }
    translate_map_literal.update ({
        0x0060: ur'\`',   # backtick should remain backtick
        0x005e: ur'\(ha', # circumflex
        0x007e: ur'\(ti', # tilde
    })
    
    def visit_Text (self, node):
        text = node.astext ()
        if self.in_literal:
            text = text.translate (self.translate_map_literal)
        else:
            text = text.translate (self.translate_map)
        text = self.re_command_dot.sub (ur"\N'46'", text) # breaking command
        text = self.re_command_apos.sub (ur"\N'39'", text) # non-breaking command
        self.text (text)

    def depart_Text (self, node):
        pass

    def visit_block (self, node, extra_classes):
        self.text (self.prefix_for_inline (extra_classes + node['classes']))

    def depart_block (self, node, extra_classes):
        self.text (self.suffix_for_inline (extra_classes + node['classes']))

    def visit_inline (self, node, extra_classes = []):
        self.text (self.prefix_for_inline (extra_classes + node['classes']))

    def depart_inline (self, node, extra_classes = []):
        self.text (self.suffix_for_inline (extra_classes + node['classes']))

    def visit_reference (self, node, extra_classes = []):
        self.text (self.prefix_for_inline (extra_classes + node['classes']))

    def depart_reference (self, node, extra_classes = []):
        self.text (self.suffix_for_inline (extra_classes + node['classes']))

    # start docinfo elements (parse only for now)
    
    def visit_docinfo (self, node):
        pass
    
    def depart_docinfo (self, node):
        pass

    def visit_authors (self, node):
        pass

    def depart_authors (self, node):
        pass

    def visit_field (self, node):
        pass

    def depart_field (self, node):
        pass

    def visit_field_name (self, node):
        self.field_name = node.astext ().lower ().replace (' ', '_')
        raise nodes.SkipNode

    def depart_field_name (self, node):
        pass

    def visit_field_body (self, node, name = None):
        # name either from element or stored by <field_name>
        self.context = self.docinfo[name or self.field_name]

    def depart_field_body (self, node):
        self.context = self.body

    def visit_field_list (self, node):
        self.sp ()
        self.push ()
        self.indent (FIELDLIST_INDENT)

    def depart_field_list (self, node):
        self.pop ()

    # start admonitions

    def visit_admonition (self, node, name = None):
        if name:
            self.text (name)
            self.sp ()
        else:
            self.br ()
        self.push ()
        self.indent (BLOCKQUOTE_INDENT)

    def depart_admonition (self, node):
        self.pop ()

    # start definition lists

    def visit_definition_list (self, node):
        self.sp ()
        self.output_sp ()
    
    def depart_definition_list (self, node):
        pass

    def visit_definition_list_item (self, node):
        pass

    def depart_definition_list_item (self, node):
        pass

    def visit_term (self, node):
        pass

    def depart_term (self, node):
        pass

    def visit_classifier (self, node):
        pass

    def depart_classifier (self, node):
        pass

    def visit_definition (self, node):
        self.up_if_last_line_shorter_than (DEFINITION_LIST_INDENT - 1)
        self.sp (0)
        self.push ()
        self.indent (DEFINITION_LIST_INDENT)

    def depart_definition (self, node):
        self.pop ()
        self.sp ()

    # start option lists
    
    def visit_option_list (self, node):
        self.sp ()
        self.output_sp ()

    def depart_option_list (self, node):
        self.output_sp ()
        self.sp ()

    def visit_option_list_item (self, node):
        pass

    def depart_option_list_item (self, node):
        pass

    def visit_option_group (self, node):
        pass

    def depart_option_group (self, node):
        pass

    def visit_option (self, node):
        pass

    def depart_option (self, node):
        if 'last' not in node['classes']:
            self.text (', ')

    def visit_option_string (self, node):
        pass

    def depart_option_string (self, node):
        pass

    def visit_option_argument (self, node):
        self.text (node.get ('delimiter', ' '))
        self.text (r'\fI')

    def depart_option_argument (self, node):
        self.text (r'\fP')

    def visit_description (self, node):
        self.up_if_last_line_shorter_than (OPTION_LIST_INDENT)
        self.sp (0)
        self.push ()
        self.indent (OPTION_LIST_INDENT)

    def depart_description (self, node):
        self.pop ()
        self.sp (0)

    # lists

    def check_simple_list (self, node):
        """Check for a simple list that can be rendered compactly."""
        try:
            node.walk (SimpleListChecker (self.document))
            return True
        except nodes.NodeFound:
            return False

    def is_compactable (self, node):
        return ('compact' in node['classes']
                or (self.settings.compact_lists
                    and 'open' not in node['classes']
                    and (# self.compact_simple or
                         # self.topic_classes == ['contents'] or
                         self.check_simple_list (node))))

    def list_start (self, node):
        if not isinstance (node.parent, nodes.list_item):
            self.sp ()
            self.output_sp () # list entry will eat all space, so output it now
            self.push ()
            self.indent (LIST_INDENT)
        self.compacting += self.is_compactable (node)
        self.list_enumerator_stack.append (writers.ListEnumerator (node, self.encoding))

    def list_end (self, node):
        self.list_enumerator_stack.pop ()
        self.compacting = max (0, self.compacting - 1)
        if not isinstance (node.parent, nodes.list_item):
            self.pop ()
            self.output_sp ()
            self.sp ()

    def visit_list_item (self, node):
        self.sp (0)
        self.br ()
        indent = self.list_enumerator_stack[-1].get_width ()
        self.ta (indent - 1, self.list_enumerator_stack[-1].get_next ())
        self.up_if_last_line_shorter_than (indent)
        self.sp (0)
        self.push ()
        self.indent (indent)

    def depart_list_item (self, node):
        self.pop ()
        if self.compacting:
            self.sp (0)
        else:
            self.sp ()
            self.output_sp ()

    def visit_bullet_list (self, node):
        self.list_start (node)

    def depart_bullet_list (self, node):
        self.list_end (node)

    def visit_enumerated_list (self, node):
        self.list_start (node)

    def depart_enumerated_list (self, node):
        self.list_end (node)

    # end lists
    
    def visit_block_quote (self, node):
        self.set_first_last (node)
        self.sp ()
        self.push ()
        self.indent (BLOCKQUOTE_INDENT)
        self.rindent (BLOCKQUOTE_INDENT)

    def depart_block_quote (self, node):
        self.pop ()
        classes = node['classes']
        if 'epigraph' in classes:
            self.sp (2)
        if 'highlights' in classes:
            self.sp (2)

    def visit_comment (self, node):
        for line in node.astext ().splitlines ():
            self.comment (line)
        raise nodes.SkipNode

    def visit_container (self, node):
        pass

    def depart_container (self, node):
        pass

    def visit_compound (self, node):
        pass

    def depart_compound (self, node):
        pass

    def visit_decoration (self, node):
        pass

    def depart_decoration (self, node):
        pass

    def visit_doctest_block (self, node):
        self.visit_literal_block (node)

    def depart_doctest_block (self, node):
        self.depart_literal_block (node)

    def visit_document (self, node):
        pass

    def depart_document (self, node):
        pass
    
    def visit_footer (self, node):
        self.document.reporter.warning (
            'footer not supported', base_node = node)

    def depart_footer (self, node):
        pass

    # footnotes, citations, labels
    
    def visit_label (self, node):
        # footnote and citation
        indent = 0
        if isinstance (node.parent, nodes.footnote):
            indent = FOOTNOTE_INDENT
        elif isinstance (node.parent, nodes.citation):
            indent = CITATION_INDENT
        else:
            self.document.reporter.warning ('label unsupported',
                base_node = node)

        try:
            label = self.as_superscript (int (node.astext ()))
        except ValueError:
            label = '[%s]' % node.astext ()

        self.ta (indent - 1, label)
        self.up_if_last_line_shorter_than (indent)
        self.sp (0)
        self.push ()
        self.indent (indent)
        raise nodes.SkipNode

    def depart_label (self, node):
        pass

    def visit_footnote (self, node):
        self.sp ()

    def depart_footnote (self, node):
        self.pop ()
        self.sp ()

    def visit_footnote_reference (self, node):
        try:
            self.text (
                self.as_superscript (int (node.astext ())))
        except ValueError:
            self.text (node.astext ())
        raise nodes.SkipNode
        
    def visit_citation (self, node):
        self.visit_footnote (node)

    def depart_citation (self, node):
        self.depart_footnote (node)

    def visit_citation_reference (self, node):
        self.text ('[%s]' % node.astext ())
        raise nodes.SkipNode

    # end footnotes

    def visit_generated (self, node):
        pass

    def depart_generated (self, node):
        pass

    def visit_header (self, node):
        self.document.reporter.warning (
            'header not supported', base_node = node)

    def depart_header (self, node):
        pass

    def visit_attribution (self, node):
        prefix, dummy_suffix = self.attribution_formats[self.settings.attribution]
        self.sp (1)
        self.output_sp ()
        self.push ()
        self.cmd ('ad r')
        self.text (prefix)

    def depart_attribution (self, node):
        dummy_prefix, suffix = self.attribution_formats[self.settings.attribution]
        self.text (suffix)
        self.pop ()
        self.sp (1)

    def visit_figure (self, node):
        self.sp (2)
        self.push ()
        self.indent (BLOCKQUOTE_INDENT)
        self.rindent (BLOCKQUOTE_INDENT)
        self.cmd ('ad c')

    def depart_figure (self, node):
        self.pop ()
        self.sp (2)

    def visit_image (self, node):
        self.text ('%s' % node.attributes.get ('alt', '[image]'))

    def depart_image (self, node):
        pass

    def visit_caption (self, node):
        self.sp ()
        self.push ()
        self.cmd ('ad c')
    
    def depart_caption (self, node):
        self.pop ()
        self.sp ()

    def visit_legend (self, node):
        self.sp ()
        self.push ()
        self.cmd ('ad l')

    def depart_legend (self, node):
        self.pop ()
        self.sp ()

    def visit_line_block (self, node):
        if not isinstance (node.parent, nodes.line_block):
            self.sp ()
        else:
            self.br ()
        self.push ()
        if isinstance (node.parent, nodes.line_block):
            self.indent ()
        self.cmd ('ad l')

    def depart_line_block (self, node):
        self.pop ()
        if not isinstance (node.parent, nodes.line_block):
            self.sp ()

    def visit_line (self, node):
        pass

    def depart_line (self, node):
        if not node.children:
            # empty lines must vspace
            self.sp ()
            self.output_sp ()
        else:
            self.br ()

    def visit_literal_block (self, node):
        self.sp ()
        self.push ()
        self.indent (BLOCKQUOTE_INDENT)
        self.cmd (('nf', 'ft C'))
        self.in_literal += 1

    def depart_literal_block (self, node):
        self.pop ()
        self.in_literal -= 1

    #
    #
    #
    
    def visit_paragraph (self, node):
        self.sp ()
        self.push ()
        if 'byline' in node['classes']:
            self.cmd ('ad c')

    def depart_paragraph (self, node):
        self.pop ()
        self.sp ()

    def visit_section (self, node):
        self.section_level += 1

    def depart_section (self, node):
        self.section_level -= 1

    def visit_raw (self, node):
        if 'nroff' in node.get ('format', '').split():
            raw = node.astext ()
            if raw[0] == '.':
                self.cmd (raw[1:])
            else:
                self.text (raw)
                
        # ignore other raw formats
        raise nodes.SkipNode

    def visit_substitution_definition (self, node):
        """Internal only."""
        raise nodes.SkipNode

    def visit_substitution_reference (self, node):
        self.document.reporter.warning ('"substitution_reference" not supported',
                base_node=node)

    def visit_target (self, node):
        # internal hyperlink target, no such thing in nroff
        raise nodes.SkipNode

    def visit_system_message (self, node):
        self.sp ()
        line = ', line %s' % node['line'] if 'line' in node else ''
        self.text ('"System Message: %s/%s (%s:%s)"'
                  % (node['type'], node['level'], node['source'], line))
        self.sp ()
        self.push ()
        self.indent (BLOCKQUOTE_INDENT)

    def depart_system_message (self, node):
        self.pop ()
        self.sp ()

    # tables
    
    def visit_table (self, node):
        self.sp (2)
        pass_1 = writers.TablePass1 (self.document)
        node.walk (pass_1)
        rows = pass_1.rows ()
        cols = pass_1.cols ()

        pass_2 = TablePass2 (self.document, node, rows, cols)
        node.walk (pass_2)
        node.pass_2 = pass_2

    def depart_table (self, node):
        self.cmd ('TE')
        self.sp (2)

    def visit_table_caption (self, node):
        self.sp ()
        self.push ()
        self.cmd ('ad c')
    
    def depart_table_caption (self, node):
        self.pop ()
    
    def visit_tgroup (self, node):
        # output this after table caption
        self.output_sp ()
        self.cmd ('TS')
        self.text ('center;\n') # table options: center
        self.text (node.parent.pass_2.build_format_spec ())

    def depart_tgroup (self, node):
        pass

    def visit_colspec (self, node):
        pass

    def depart_colspec (self, node):
        pass

    def visit_thead (self, node):
        self.set_first_last (node) # mark first row of head
        self.text ('=\n')

    def depart_thead (self, node):
        self.text ('=\n')

    def visit_tbody (self, node):
        self.set_first_last (node) # mark first row of body

    def depart_tbody (self, node):
        self.text ('=')

    def visit_row (self, node):
        self.set_first_last (node) # mark first and last cell
        if 'first' not in node['classes']:
            if 'norules' in node.parent.parent.parent['classes']:
                self.cmd ('sp')
            else:
                self.text ('_\n')

    def depart_row (self, node):
        pass

    def visit_entry (self, node):
        if 'first' in node['classes']:  # first cell in row
            self.text ('T{\n')
            self.sp (0)
            self.last_output_type = 'cmd' # avoids superfluous \n

    def depart_entry (self, node):
        self.sp (0)
        if self.last_output_type == 'text':
            self.context.append ('\n')
        if 'last' in node['classes']:  # last cell in row
            self.text ('T}\n')
        else:
            self.text ('T}\tT{\n')
            self.sp (0)
        self.last_output_type = 'cmd'
            

    # end tables

    def visit_document_title (self, node):
        self.br ()
        self.push ()
        self.cmd ('ad c')
    
    def depart_document_title (self, node):
        if 'with-subtitle' in node['classes']:
            self.sp (1)
        else:
            self.sp (2)
        self.pop ()

    def visit_document_subtitle (self, node):
        self.sp (1)
        self.push ()
        self.cmd ('ad c')
    
    def depart_document_subtitle (self, node):
        self.pop ()
        self.sp (2)

    def visit_section_title (self, node):
        self.sp (3)
        
    def depart_section_title (self, node):
        self.sp (2)

    def visit_section_subtitle (self, node):
        self.sp (1)
    
    def depart_section_subtitle (self, node):
        self.sp (2)

    def visit_topic (self, node):
        self.sp (4)

    def depart_topic (self, node):
        self.sp (4)

    def visit_topic_title (self, node):
        pass

    def depart_topic_title (self, node):
        self.sp (2)

    def visit_sidebar (self, node):
        pass

    def depart_sidebar (self, node):
        pass

    def visit_rubric (self, node):
        pass

    def depart_rubric (self, node):
        pass

    def visit_transition (self, node):
        self.sp ()
        self.cmd ('ce 1')
        self.text (u'————' if self.encoding == 'utf-8' else '----')
        self.sp ()

    def depart_transition (self, node):
        pass

    def visit_page (self, node):
        if 'vspace' in node['classes']:
            self.sp (node['length'])
        elif 'clearpage' in node['classes']:
            self.cmd ('bp')
        elif 'cleardoublepage' in node['classes']:
            self.cmd ('bp')
        elif 'vfill' in node['classes']:
            self.sp (4)

    def depart_page (self, node):
        pass

    def visit_problematic (self, node):
        self.cmd ('nf')

    def depart_problematic (self, node):
        self.cmd ('fi')

    def visit_meta (self, node):
        raise NotImplementedError, node.astext ()

    def unimplemented_visit (self, node):
        raise NotImplementedError ('visiting unimplemented node type: %s'
                                  % node.__class__.__name__)
