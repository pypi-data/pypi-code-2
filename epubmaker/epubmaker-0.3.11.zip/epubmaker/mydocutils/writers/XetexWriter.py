# -*- coding: utf-8 -*-
# Copyright: This module is put into the public domain.
# Author: Marcello Perathoner <webmaster@gutenberg.org>

"""
Xetex writer for reStructuredText.

This module is more suitable for writing novel-type books than
documentation.

"""

# ß fix table and column width in nroff
# ß fix paragraphs in latex tables
# add thinspace between quotes
# add struts in html titles + line-height ?
# use old-style figures in pdf
# list of figures, list of tables
# boxes around examples

__docformat__ = 'reStructuredText'

import operator
import re

from docutils import nodes, frontend
from docutils.writers.html4css1 import SimpleListChecker

from epubmaker.lib.Logger import error, info, debug, warn
from epubmaker.lib import DublinCore
from epubmaker.Version import VERSION

from epubmaker.mydocutils import writers
from epubmaker.mydocutils.transforms import parts

XETEX_PREAMBLE = r"""% -*- mode: tex -*- coding: utf-8 -*-
% Converted from RST master
%
\documentclass[a5paper]{book}

\usepackage{polyglossia}
\setdefaultlanguage{english}

\usepackage{xltxtra}

\defaultfontfeatures{Scale=MatchLowercase}
\setmainfont{Linux Libertine O}
\setsansfont{Linux Biolinum O}
\setmonofont[HyphenChar=None]{DejaVu Sans Mono}

\usepackage{calc}
\usepackage{graphicx}
\usepackage{multirow}
\usepackage{alltt}

\usepackage{longtable}

\usepackage{booktabs}
\newcommand{\otoprule}{\midrule[\heavyrulewidth]}

\usepackage{lettrine} % dropcaps
\usepackage[implicit=false,colorlinks=true,linkcolor=blue]{hyperref}
<hypersetup>
\usepackage[open,openlevel=1]{bookmark}

\tolerance 10000  % dont make overfull boxes
\hbadness 1000    % warn if badness exceeds 1000

\catcode`@=11     % make 'private' LaTeX variables public
\catcode`\^^J=10  % don't let empty lines end paragraphs
\catcode`\^^M=10
\catcode`\"=12    % no electric quotes

\setlength{\textwidth} {\paperwidth  * 7 / 9}
\setlength{\textheight}{\paperheight * 7 / 9}

\setlength{\topmargin}     {\paperheight / 9 - \topskip - \headsep - \headheight - 1in}

\setlength{\evensidemargin}{\paperwidth / 9 - 1in}
\setlength{\oddsidemargin} {\paperwidth / 9 - 1in}


\begin{document}

\setlength{\parindent}{24pt}
\setlength{\parskip}{0pt}
\setlength{\parsep}{0pt}
\setlength{\topsep}{0pt plus6pt}
\setlength{\footnotesep}{0pt}

\setcounter{LTchunksize}{10000} % process tables in one chunk

% pagination
\renewcommand*{\ps@plain}{
 \renewcommand*{\@evenhead}{}
 \renewcommand*{\@oddhead}{}
 \renewcommand*{\@oddfoot}{}
 \renewcommand*{\@evenfoot}{}
}

\newcommand*{\docutilstitle}{}

\newcommand*{\ps@docutils}{
 \renewcommand*{\@evenhead}{\thepage\hfil\docutilstitle}
 \renewcommand*{\@oddhead}{\firstmark\hfil\thepage}
 \renewcommand*{\@oddfoot}{}
 \renewcommand*{\@evenfoot}{}
}

% redefine cleardoublepage to output a completely blank page
\let\cdpage\cleardoublepage
\renewcommand*{\cleardoublepage}{
 \clearpage
 {\pagestyle{plain}\cdpage}
}

% headers

% HACK! to avoid a page break between labels and section title
% standard secpenalty is -300
\@secpenalty = 0

\setcounter{secnumdepth}{-1} % no automatic section numbering
% \setcounter{tocdepth}{1} we don't use auto toc at present

\def\pgpageno#1{\marginpar[\hfill\fbox{#1}]{\fbox{#1}}}

\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
  \sbox\@tempboxa{#2}%
  \ifdim \wd\@tempboxa >\hsize
    #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}
  
\setlength{\belowcaptionskip}{\smallskipamount}

% use the lineblock environment for titlepages etc.
% the indentation specified in the latex verse environment
% gets in the way if we try to center.

\newenvironment{lineblock}
  {%
    \let\\\@centercr
    \list{}{}%
    \item\relax
  }%
  {%
    \endlist
  }

\def\startenv{%
  \clearpage
  \if@twocolumn
    \@restonecoltrue\onecolumn
  \else
    \@restonecolfalse\newpage
  \fi
  \thispagestyle{empty}%
}
\def\endenv{%
  \if@restonecol\twocolumn \else \newpage \fi     
}

\newenvironment{pgheader}
  {%
    \thispagestyle{empty}%
  }{%
    \endenv
  }

\newenvironment{coverpage}{\cleardoublepage\startenv}{\endenv}
\newenvironment{frontispiece}{\startenv}{\endenv}
\newenvironment{verso}{\startenv}{\endenv}
\newenvironment{dedication}{\startenv}{\endenv}
\newenvironment{plainpage}{\startenv}{\endenv}

\renewenvironment{titlepage}
  {%
    \cleardoublepage
    \startenv
    \setcounter{page}\@ne
  }{%
    \endenv
    \if@twoside\else
      \setcounter{page}\@ne
    \fi
  }

\newdimen{\tablewidth} % helper

% \tracingpages=1

\frontmatter
\thispagestyle{plain}

"""

XETEX_POSTAMBLE = r"""
\end{document}

% Local Variables:
% mode: tex
% encoding: utf-8
% End:
"""

BLOCKQUOTE_INDENT      =  4
LIST_INDENT            =  2
FOOTNOTE_INDENT        =  5
CITATION_INDENT        = 10
FIELDLIST_INDENT       =  7
DEFINITION_LIST_INDENT =  7
OPTION_LIST_INDENT     =  7

class Writer (writers.Writer):
    """ A xetex/pdf writer. """

    supported = ('xetex',)
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    settings_spec = (
        'Xetex-Specific Options',
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
         ))

    config_section = 'XeTeX writer'
    
    config_section_dependencies = ('writers',)


    def get_transforms (self):
        tfs = writers.Writer.get_transforms (self)
        return tfs + [parts.XetexFootnotesTransform, parts.XetexMetaCollector]


    def __init__ (self):
        writers.Writer.__init__ (self)
        self.translator_class = Translator


    def translate (self):
        visitor = self.translator_class (self.document)
        self.document.walkabout (visitor)
        self.output = visitor.astext ()


class MakeTableRules (nodes.SparseNodeVisitor):

    """
    Makes a pass over a table row to output rules.
    """
    
    def __init__ (self, document, translator):
        nodes.SparseNodeVisitor.__init__ (self, document)
        self.translator = translator

    def visit_entry (self, node):
        """ Called on each table cell. """

        firstcol = node['column']
        lastcol = firstcol + len (node.colspecs) - 1
        self.translator.cmd (r'\cmidrule{%d-%d}' % (firstcol + 1, lastcol + 1)) # 1-based

        
class TablePass2 (nodes.SparseNodeVisitor):

    """
    Makes a second pass over table to build xetex format specifications.
    """
    
    def __init__ (self, table, rows, cols):
        nodes.SparseNodeVisitor.__init__ (self, table)
        self.cols = cols
        self.header_sent = False

    def begin_tabular (self, translator, table):
        """ Table implementation using longtable. """
        
        if self.header_sent:
            return

        if 'colspec' in table:
            colspec = table['colspec']
        else:
            colspecs = table.traverse (nodes.colspec)
            ## width = sum (map (operator.itemgetter ('colwidth'), colspecs))
            ## for colspec in colspecs:
            ##     colspec['relative_width'] = float (colspec['colwidth']) / width
            colspec = 'l' * len (colspecs)

        translator.cmd (r'\setlength{\tablewidth}{%s - \tabcolsep * 2 * %d}' % (
                        translator.latex_units (table['width'], '\\linewidth'), len (colspecs)))
        
        translator.begin ('longtable', r'{%s}' % (colspec))

        self.header_sent = True


    def begin_tabulary (self, translator, table):
        """ Table implementation using tabulary. """
        if self.header_sent:
            return

        res = []

        if 'colspec' in table:
            colspec = table['colspec']
        else:
            colspecs = table.traverse (nodes.colspec)
            width = sum (map (operator.itemgetter ('colwidth'), colspecs))

            for colspec in colspecs:
                align = colspec.get ('align', 'justify')[0].upper ()
                colwidth = float (colspec['colwidth']) / width
                res.append (r'>{\hsize=%.03f\tablewidth\advance\hsize-2\tabcolsep}%s' % (colwidth, align))
                # res.append (r'>{\hsize=%.03f\hsize}%s' % (colwidth * len (colspecs), align))

            colspec = (''.join (res))

        translator.cmd (r'\setlength{\tablewidth}{%s}' %
                        translator.latex_units (table['width'], '\\linewidth'))
        
        translator.begin ('tabulary', r'{\tablewidth}{%s}' % (colspec))

        self.header_sent = True


class ContentsFilter(nodes.TreeCopyVisitor):

    def visit_citation_reference(self, node):
        raise nodes.SkipNode

    def visit_footnote_reference(self, node):
        raise nodes.SkipNode

    def visit_image(self, node):
        if node.hasattr('alt'):
            self.parent.append(nodes.Text(node['alt']))
        raise nodes.SkipNode

    def ignore_node_but_process_children(self, node):
        raise nodes.SkipDeparture

    visit_interpreted = ignore_node_but_process_children
    visit_problematic = ignore_node_but_process_children
    visit_reference = ignore_node_but_process_children
    visit_target = ignore_node_but_process_children

    
class Translator (writers.Translator):
    """ XeTeX translator """

    section_commands = """
    chapter section subsection subsubsection paragraph subparagraph
    """.split ()

    def __init__ (self, document):
        writers.Translator.__init__ (self, document)

        self.forbidden = '' # temporary hold for statements that are forbidden
                            # in environments. eg. footnotes inside tables.
        self.bookmarks = [] # hold bookmarks until end of document
        self.toc_depth = 2  # when should we set pdf bookmarks

        self.attribution_formats['dash'] = (u'― ', '')
        

    def register_classes (self):
        """ Register classes. """
        
        # register classes in the order you want them applied!

        # outside block classes

        # mayor building blocks
        self.register_block_class  ('pgheader',     '\n\\begin{pgheader}\n',      '\n\\end{pgheader}\n')
        self.register_block_class  ('coverpage',    '\n\\begin{coverpage}\n',     '\n\\end{coverpage}\n')
        self.register_block_class  ('frontispiece', '\n\\begin{frontispiece}\n',  '\n\\end{frontispiece}\n')
        self.register_block_class  ('titlepage',    '\n\\begin{titlepage}\n',     '\n\\end{titlepage}\n')
        self.register_block_class  ('verso',        '\n\\begin{verso}\n',         '\n\\end{verso}\n')
        self.register_block_class  ('plainpage',    '\n\\begin{plainpage}\n',     '\n\\end{plainpage}\n')

        # minor
        self.register_block_class  ('example-rendered', '\n\\begin{quote}\n',     '\n\\end{quote}\n')

        # inside block classes
        
        self.register_inline_class ('align-left',  '\\begin{flushleft}\n',  '\\end{flushleft}\n')
        self.register_inline_class ('align-right', '\\begin{flushright}\n', '\\end{flushright}\n')
        self.register_inline_class ('align-center','\\begin{center}\n',     '\\end{center}\n')
        
        self.register_inline_class ('left',  '\\begin{flushleft}\n',  '\n\\end{flushleft}\n')
        self.register_inline_class ('right', '\\begin{flushright}\n', '\n\\end{flushright}\n')
        self.register_inline_class ('center','\\begin{center}\n',     '\n\\end{center}\n')
        
        self.register_inline_class ('minipage',    '\\begin{minipage}{\dimen0}\n', '\\end{minipage}\n')
        
        # self.register_inline_class ('pfirst',      '\\noindent\n',   r'')
        self.register_inline_class ('noindent',    '\\noindent\n',   r'')

        # inline classes
        
        self.register_inline_class ('superscript', r'\textsuperscript{', r'}')
        self.register_inline_class ('subscript',   r'\textsubscript{',   r'}')
        
        self.register_inline_class ('italics',     r'{\itshape ',        r'}')
        self.register_inline_class ('bold',        r'{\bfseries ',       r'}')
        self.register_inline_class ('monospaced',  r'{\ttfamily ',       r'}')
        self.register_inline_class ('small-caps',  r'{\scshape ',        r'}')
        self.register_inline_class ('normal',      r'{\upshape ',        r'}')
        self.register_inline_class ('antiqua',     r'{\upshape ',        r'}')

        self.register_inline_class ('gesperrt',    r'{\addfontfeature{LetterSpace=20.0}',  r'}')
        
        self.register_inline_class ('larger',      r'{\addfontfeature{Scale=1.2}',         r'}')
        self.register_inline_class ('smaller',     r'{\addfontfeature{Scale=0.8}',         r'}')

        self.register_inline_class ('xx-large',    r'{\Huge ',         r'}')
        self.register_inline_class ('x-large',     r'{\LARGE ',        r'}')
        self.register_inline_class ('large',       r'{\Large ',        r'}')
        self.register_inline_class ('medium',      r'{\normalsize ',   r'}')
        self.register_inline_class ('small',       r'{\footnotesize ', r'}')
        self.register_inline_class ('x-small',     r'{\scriptsize ',   r'}')
        self.register_inline_class ('xx-small',    r'{\tiny ',         r'}')

        self.register_inline_class ('red',         r'{\addfontfeature{Color=FF0000}',      r'}')
        self.register_inline_class ('green',       r'{\addfontfeature{Color=00FF00}',      r'}')
        self.register_inline_class ('blue',        r'{\addfontfeature{Color=0000FF}',      r'}')
        self.register_inline_class ('yellow',      r'{\addfontfeature{Color=FFFF00}',      r'}')
        self.register_inline_class ('white',       r'{\addfontfeature{Color=FFFFFF}',      r'}')
        self.register_inline_class ('gray',        r'{\addfontfeature{Color=808080}',      r'}')
        self.register_inline_class ('black',       r'{\addfontfeature{Color=000000}',      r'}')


    def cmd (self, cmds):
        """ Output tex commands. """
        if isinstance (cmds, basestring):
            cmds = [cmds]

        ## if self.last_output_type == 'text':
        ##    self.context.append ('\n')
        for c in cmds:
            self.context.append (c)
        self.last_output_type = 'cmd'
        
    def text (self, text):
        """ Output text. """
        ## self.output_sp () # inline elements should never sp ()
        self.context.append (text)
        self.last_output_type = 'text'

    def comment (self, text):
        """ Output tex comment. """
        self.context.append ('%% %s\n' % text)
        self.last_output_type = 'cmd'

    def output_sp (self):
        """ Output spacing and pending stuff. """
        if self.vspace == 1999: # magic number to eat all space
            self.vspace = 0
        if self.vspace:
            self.cmd ('\\vspace{%dem}\n' % self.vspace)
            self.vspace = 0

    def ta (self, indent, text):
        """ Tabulate text to indent position. """
        self.cmd (r'\hspace{%dem}\=\kill' % indent)
        self.text (r'\+' + text)
        
    def begin (self, name = None, param = None):
        """ Push environment. """
        self.output_sp ()
        self.environments.append (name)
        if name:
            self.cmd ('\n\\begin{%s}%s\n' % (name, param or ''))
        else:
            self.cmd ('{') # put no nl here! may be used for inline nodes
        
    def end (self):
        """ Pop environment. """
        name = self.environments.pop ()
        if name:
            self.cmd ('\n\\end{%s}\n' % name)
        else:
            self.cmd ('}') # put no nl here!
        
    def filter_title (self, node):
        """ Return a copy of a title, with references, images, etc. removed."""
        visitor = ContentsFilter (self.document)
        node.walkabout (visitor)
        return visitor.get_tree_copy ()

    def get_align (self, node):
        return node.colspecs[0].get ('align', 'justify')[0] # .upper ()

    def up_if_last_line_shorter_than (self, length):
        """ Go one line up if the last line was shorter than length.

        Use this to compact lists etc. """
        # FIXME: how do we go up in TeX?
        # \pdfsavepos
        # 'if \pdflastxpos < %dem' % length
        
    def indent (self, by = 2):
        """ Indent text. """
        self.cmd (r'\advance\leftskip%dem{}' % by)

    def rindent (self, by = 2):
        """ Indent text on the right side. """
        self.cmd (r'\advance\rightskip%dem{}' % by)

    # pylint: disable=C0111
    # pylint: disable=W0613

    translate_map = translate_map_literal = {
        ord ('#'):  ur'\#',
        ord ('$'):  ur'\$',
        ord ('%'):  ur'\%',
        ord ('&'):  ur'\&',
        ord ('~'):  ur'\textasciitilde{}',
        ord ('_'):  ur'\_',
        ord ('^'):  ur'\textasciicircum{}',
        ord ('\\'): ur'\textbackslash{}',
        ord ('{'):  ur'\{',
        ord ('}'):  ur'\}',
        ord ('['):  ur'{[}',
        ord (']'):  ur'{]}',
        0x00ad:     ur'\-', # soft hyphen
    }
    translate_map_literal.update ({
        0x0d:       u'\\\\n',
    })
    
    def preamble (self):
        """ Inserts xetex preamble. """
        
        hs = ['\\hypersetup{pdfcreator={Project Gutenberg EpubMaker %s}}' % VERSION]
        if hasattr (self.document, 'meta_block'):
            for name, values in self.document.meta_block.iteritems ():
                if name.lower () == 'dc.title':
                    content = values[0]
                    hs.append ('\\hypersetup{pdftitle={%s}}' % content)
                elif name.lower () == 'dc.creator':
                    content = DublinCore.DublinCore.strunk (values)
                    hs.append ('\\hypersetup{pdfauthor={%s}}' % content)
                elif name.lower () == 'dc.subject':
                    content = DublinCore.DublinCore.strunk (values)
                    hs.append ('\\hypersetup{pdfsubject={%s}}' % content)
        
        return XETEX_PREAMBLE.replace ('<hypersetup>', '\n'.join (hs))

    def postamble (self):
        """ Inserts xetex postamble. """
        return XETEX_POSTAMBLE

    def write_labels (self, node):
        """ Write labels for all ids of `node` """
        for id_ in node['ids']:
            self.cmd ('\\label{%s}%%\n' % id_)
            self.cmd ('\\hypertarget{%s}{}%%\n' % id_)

    def latex_units (self, length_str, reference_length = ''):
        """ Convert rst units to LaTeX units. """
        
        match = re.match ('(\d*\.?\d*)\s*(\S*)', length_str)
        if not match:
            return length_str
        
        value, unit = match.groups ()
        # no unit or "DTP" points (called 'bp' in TeX):
        if unit in ('', 'pt'):
            length_str = '%sbp' % value
            
        # percentage: relate to current line width
        elif unit == '%':
            length_str = '%.3f%s' % (float (value) / 100.0, reference_length)
            
        return length_str

    # begin visitor functions

    def pre_visit_block (self, node):
        self.text (self.prefix_for_block (node['classes']))

    def post_depart_block (self, node):
        self.text (self.suffix_for_block (node['classes']))

    def visit_block (self, node, extra_classes):
        self.text (self.prefix_for_inline (extra_classes + node['classes']))

    def depart_block (self, node, extra_classes):
        self.text (self.suffix_for_inline (extra_classes + node['classes']))

    def visit_inline (self, node, extra_classes = []):
        if 'toc-pageref' in node['classes']:
            self.cmd (r'\leaders\hbox to 1em{\hss.\hss}\hfill{}')
        if 'dropcap' in node['classes']:
            self.lettrine (node)
        self.text (self.prefix_for_inline (extra_classes + node['classes']))

    def depart_inline (self, node, extra_classes = []):
        self.text (self.suffix_for_inline (extra_classes + node['classes']))
        if 'dropcap' in node['classes']:
            self.cmd (r'}')

    def encode (self, text):
        return text.translate (self.translate_map)
    
    def visit_Text (self, node):
        text = node.astext ()
        if self.in_literal:
            text = text.translate (self.translate_map_literal)
        else:
            text = text.translate (self.translate_map)
        self.text (text)

    def depart_Text (self, node):
        pass

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
        self.begin ()
        self.indent (FIELDLIST_INDENT)

    def depart_field_list (self, node):
        self.end ()

    # start admonitions

    def visit_admonition (self, node, name = None):
        self.begin ('quote')
        if name:
            self.cmd ('\\textbf{')
            self.text (name)
            self.cmd ('}\\par\n\n')

    def depart_admonition (self, node):
        self.end ()

    # start definition lists

    def visit_definition_list (self, node):
        self.begin ('description')
    
    def depart_definition_list (self, node):
        self.end ()

    def visit_definition_list_item (self, node):
        pass

    def depart_definition_list_item (self, node):
        pass

    def visit_term (self, node):
        self.cmd ('\\item[')

    def depart_term (self, node):
        self.cmd ('] ')

    def visit_classifier (self, node):
        pass

    def depart_classifier (self, node):
        pass

    def visit_definition (self, node):
        pass

    def depart_definition (self, node):
        pass

    # start option lists
    
    def visit_option_list (self, node):
        pass

    def depart_option_list (self, node):
        pass

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
        if not 'italics' in node['classes']:
            node['classes'].append ('italics')
        self.visit_inline (node)

    def depart_option_argument (self, node):
        self.depart_inline (node)

    def visit_description (self, node):
        pass

    def depart_description (self, node):
        pass

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
        self.begin ('itemize')
        self.list_enumerator_stack.append (writers.ListEnumerator (node, 'utf-8'))

    def list_end (self, node):
        self.list_enumerator_stack.pop ()
        self.end ()

    def visit_list_item (self, node):
        if 'toc-entry' in node['classes']:
            self.cmd (r'\item[] ')
        else:
            self.cmd (r'\item[%s] ' % self.list_enumerator_stack[-1].get_next ())

    def depart_list_item (self, node):
        pass

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
        self.begin ('quote')

    def depart_block_quote (self, node):
        self.end ()

    def visit_comment (self, node):
        for line in node.astext ().splitlines ():
            self.comment (line)
        raise nodes.SkipNode

    def visit_container (self, node):
        self.begin ()

    def depart_container (self, node):
        self.end ()

    def lettrine (self, node):
        # node is inline or image
        options = []
        if 'lines' in node:
            options.append ('lines=%d' % node['lines'])
        if 'indents' in node:
            indents = node['indents'].split ()
            if len (indents) < 2:
                indents.append ('0.5em')
            self.cmd (r'\dimen0=%s\dimen1=%s\advance\dimen1-\dimen0'
                      % (indents[0], indents[1]))
            options.append ('findent=\dimen0')
            options.append ('nindent=\dimen1')
                
        uri = node.get ('image', '')
        if uri:
            options.append ('image')
        self.cmd (r'\clubpenalty\@M\lettrine[%s]{' % ','.join (options))
        if uri:
            self.cmd (uri)
            self.cmd ('}')
            raise nodes.SkipNode
            
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
        header_done = False
        for target in node.traverse (nodes.target, descend=1):
            if 'pageno' in target['classes']:
                if not header_done:
                    self.bookmarks.append ('\\bookmark[level=1,page=1]{Original Page Numbers}\n')
                    header_done = True
                options = { 'class': 'target' }
                pageno = target['html_attributes']['title']
                self.write_pdf_bookmark (target, pageno, 2)
        
        self.cmd (''.join (self.bookmarks))
        
    
    def visit_footer (self, node):
        self.document.reporter.warning (
            'footer not supported', base_node = node)

    def depart_footer (self, node):
        pass

    # footnotes, citations, labels
    
    def visit_label (self, node):
        # footnote and citation
        self.cmd ('\\footnotetext[%s]\n' % node.astext ())
        self.begin ()
        raise nodes.SkipNode

    def depart_label (self, node):
        pass

    def visit_footnote (self, node):
        pass

    def depart_footnote (self, node):
        self.end ()

    def visit_footnote_reference (self, node):
        self.cmd (r'\footnotemark[')
        
    def depart_footnote_reference (self, node):
        self.cmd (']')
        
    def visit_citation (self, node):
        self.visit_footnote (node)

    def depart_citation (self, node):
        self.depart_footnote (node)

    def visit_citation_reference (self, node):
        self.cmd (r'\cite{')

    def depart_citation_reference (self, node):
        self.cmd (r'}')

    # end footnotes

    # references and targets
    
    def visit_reference (self, node):
        # we don't support extrnal refs
        if 'refuri' in node:
            href = None
        # internal reference
        elif 'refid' in node:
            href = node['refid']
        elif 'refname' in node:
            href = self.document.nameids[node['refname']]
        else:
            raise AssertionError ('Unknown reference.')
        if href:
            self.cmd ('\\hyperlink{%s}' % href)
        self.begin ()

    def depart_reference (self, node):
        self.end ()

    def visit_target (self, node):
        if 'pageno' in node['classes']:
            options = { 'class': 'target' }
            pageno = node['html_attributes']['title']
            if 'invisible' not in node['classes']:
                cmd  = '\\pgpageno{%s}' % pageno
                if 'figure' in self.environments:
                    self.forbidden += cmd
                else:
                    self.cmd (cmd)
            self.output_sp ()
            self.cmd ('\\raisebox{1em}')
            self.begin ()
            
                    
        # skip indirect targets
        #if ('refuri' in node       # external hyperlink
        #    or 'refid' in node     # resolved internal link
        #    or 'refname' in node): # unresolved internal link
        #    self.begin ()
        #    return

        self.write_labels (node)
        self.begin ()

    def depart_target(self, node):
        if 'pageno' in node['classes']:
            self.end ()
        self.end ()

    # end references and targets

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
        self.cmd ('\\nopagebreak\n\n\\raggedleft ')
        self.text (prefix)

    def depart_attribution (self, node):
        dummy_prefix, suffix = self.attribution_formats[self.settings.attribution]
        self.text (suffix + '\\\\\n')

    def visit_figure (self, node):
        float_options = 'htbp'
        if isinstance (node.parent, nodes.container):
            float_options = 'h!'
        
        self.begin ('figure', '[%s]' % float_options)
        if 'width' in node: # figwidth
            node['classes'].append ('minipage')
            self.cmd ('\dimen0=%s\n' % self.latex_units (node['width'], '\\textwidth'))
            image = node[0]
            if not 'width' in image:
                image['width'] = '100%'
        
        self.forbidden = ''

    def depart_figure (self, node):
        self.end ()
        self.cmd (self.forbidden)
        self.forbidden = ''

    def visit_image (self, node):
        if 'dropcap' in node['classes']:
            self.lettrine (node)
        
        align = node.get ( # set default alignment in a figure to 'center'
            'align', 'center' if isinstance (node.parent, nodes.figure) else '')

        image_align_codes = {
            # inline images: by default latex aligns the bottom.
            'bottom': r'%s',
            'middle': r'\raisebox{-0.5\height}{%s}',
            'top':    r'\raisebox{-\height}{%s}',
            # block level images:
            'center': '\\begin{center}\n%s\n\\end{center}\n',
            'left':   r'{\noindent%s\hfill\noindent}',
            'right':  r'{\noindent\hfill%s\noindent}',
            }

        options = []
        if 'height' in node:
            options.append ('height=%s' % self.latex_units (node['height']))
        if 'scale' in node:
            options.append ('scale=%f'  % (node['scale'] / 100.0))
        if 'width' in node:
            options.append ('width=%s'  % self.latex_units (node['width'], '\\textwidth'))

        options = (options and '[%s,keepaspectratio=true]' % (','.join (options))) or ''
        command = '\\includegraphics%s{%s}' % (options, node['uri'])

        if align in image_align_codes:
            command = image_align_codes[align] % command
            
        self.cmd (command)


    def depart_image(self, node):
        if 'dropcap' in node['classes']:
            self.cmd ('}')
        self.write_labels (node)

    def depart_image (self, node):
        pass

    def visit_caption (self, node):
        self.begin ('center')
    
    def depart_caption (self, node):
        self.end ()

    def visit_legend (self, node):
        self.sp ()

    def depart_legend (self, node):
        self.sp ()

    def visit_line_block (self, node):
        if not isinstance (node.parent, nodes.line_block):
            if 'center' in node['classes']:
                self.begin ('lineblock')
            else:
                self.begin ('verse')
        else:
            self.begin ()
            self.indent ()

    def depart_line_block (self, node):
        self.end ()

    def visit_line (self, node):
        pass

    def depart_line (self, node):
        if len (node.astext ()) == 0:
            # empty lines must use \vspace or latex
            # will complain about no line to end
            self.cmd ('\\vspace*{1em}\n')
        else:
            self.cmd (' \\\\\n')

    def visit_literal_block (self, node):
        self.begin ('quote')
        self.begin ('alltt')
        self.in_literal += 1

    def depart_literal_block (self, node):
        self.in_literal -= 1
        self.end ()
        self.end ()

    #
    #
    #
    
    def visit_paragraph (self, node):
        self.output_sp ()
        #if 'pnext' in node['classes'] and 'noindent' not in node['classes']:
        #    self.cmd ('\\hspace*{1cm}')

    def depart_paragraph (self, node):
        # The LaTeX `\footnote` macro appends a strut to the footnote
        # text to ensure correct spacing if the last line of the
        # footnote text has no descenders. If we end the footnote with
        # a \par the strut after the \par will yield an empty line.
        # The same is true for table cells.
        if isinstance (node.parent, (nodes.footnote, nodes.entry)):
            if not node.next_node (descend = 0, siblings = 1):
                return
        self.cmd ('\\par\n\n')

    def visit_raw (self, node):
        if 'tex' in node.get ('format', '').split():
            self.cmd (node.astext ())
                
        # ignore other raw formats
        raise nodes.SkipNode

    def visit_substitution_definition (self, node):
        """Internal only."""
        raise nodes.SkipNode

    def visit_substitution_reference (self, node):
        self.document.reporter.warning ('"substitution_reference" not supported',
                base_node=node)

    def visit_system_message (self, node):
        self.begin ('quote')
        line = ', line %s' % node['line'] if 'line' in node else ''
        self.text ('"System Message: %s/%s (%s:%s)"'
                  % (node['type'], node['level'], node['source'], line))

    def depart_system_message (self, node):
        self.end ()

    # tables
    
    def visit_table (self, node):
        pass_1 = writers.TablePass1 (self.document)
        node.walk (pass_1)
        rows = pass_1.rows ()
        cols = pass_1.cols ()

        pass_2 = TablePass2 (self.document, rows, cols)
        node.walk (pass_2)
        node.pass_2 = pass_2

        self.begin ('table', '[htbp]')
        self.cmd ('\\footnotesize\n')

    def depart_table (self, node):
        self.end ()

    def visit_table_caption (self, node):
        self.cmd ('\\caption')
        self.begin ()
    
    def depart_table_caption (self, node):
        self.end ()
    
    def visit_tgroup (self, node):
        pass

    def depart_tgroup (self, node):
        pass

    def visit_colspec (self, node):
        pass

    def depart_colspec (self, node):
        pass

    def visit_thead (self, node):
        node.parent.parent.pass_2.begin_tabular (self, node.parent.parent)
        self.set_first_last (node) # mark first row of head
        self.cmd ('\\toprule\n')

    def depart_thead (self, node):
        pass

    def visit_tbody (self, node):
        node.parent.parent.pass_2.begin_tabular (self, node.parent.parent)
        self.set_first_last (node) # mark first row of body
        self.cmd ('\\otoprule\n')

    def depart_tbody (self, node):
        self.cmd ('\\bottomrule\n')
        self.end ()

    def visit_row (self, node):
        self.set_first_last (node) # mark first and last cell
        if 'first' not in node['classes']:
            if 'norules' in node.parent.parent.parent['classes']:
                self.cmd ('\\addlinespace[0pt]\n')
            else:
                make_rules = MakeTableRules (self.document, self)
                node.walk (make_rules)
                self.cmd ('\n')

    def depart_row (self, node):
        self.cmd ('\\tabularnewline\n')

    def visit_entry (self, node):

        width = sum (map (operator.itemgetter ('relative_width'), node.colspecs))
        
        cols = node.get ('morecols', 0)
        if cols:
            # multicol
            self.cmd (r'\setlength{\dimen0}{%.03f\tablewidth + \tabcolsep * %d * 2}' % (width, cols))
            self.cmd (r'\hbox to %.03f\tablewidth' % node.colspecs[0]['relative_width'])
        else:
            self.cmd (r'\setlength{\dimen0}{%.03f\tablewidth}' % width)
                     
        self.begin ()

        rows = node.get ('morerows', 0) + 1
        if rows > 1:
            self.cmd (r'\multirow{%d}{\dimen0}' % rows)
            self.begin ()

        self.cmd (r'\parbox{\dimen0}')
        self.begin ()
        self.cmd ({ 'left'   : '\\raggedright ',
                    'right'  : '\\raggedleft ',
                    'center' : '\\centering ',
                    'justify': '' }[node.colspecs[0].get ('align', 'justify')])

        if isinstance (node.parent.parent, nodes.thead):
            self.cmd ('\\bfseries')
            
        self.cmd (r'\setlength{\parskip}{1em}\noindent')
        self.cmd (r'\@arstrut{}')

    def depart_entry (self, node):
        self.cmd (r'\@arstrut')
        rows = node.get ('morerows', 0) + 1
        if rows > 1:
            self.end ()
        self.end ()
        self.end ()
        self.cmd (' &' * node.get ('morecols', 0))
        if 'last' not in node['classes']:  # not last cell in row
            self.cmd (' & ')
            

    # end tables

    def visit_document_title (self, node):
        self.begin ('center')
    
    def depart_document_title (self, node):
        if 'with-subtitle' in node['classes']:
            self.sp (1)
        else:
            self.sp (2)
        self.end ()

    def visit_document_subtitle (self, node):
        self.sp (1)
        self.begin ('center')
    
    def depart_document_subtitle (self, node):
        self.end ()
        self.sp (2)

    def visit_section (self, node):
        self.section_level += 1
        if 'toc_depth' in node:
            self.toc_depth = node['toc_depth']

    def depart_section (self, node):
        self.section_level -= 1

    def write_pdf_bookmark (self, node, title, level = None):
        if node['ids']:
            if level is None:
                level = self.section_level
            self.bookmarks.append (
                '\\bookmark[level=%d,dest=%s]{%s}\n' % (
                    level, node['ids'][0], self.encode (title)))
            
    def visit_section_title (self, node):
        eff_level = min (self.section_level, 6) - 1 # 0-based
        section_command = self.section_commands [eff_level]
        section = node.parent

        if 'toc_entry' in  node:
            short_title = node['toc_entry']
        else:
            short_title = self.filter_title (node).astext ()

        if eff_level == 0:
            self.cmd ('\\cleardoublepage\n')
        else:
            self.cmd ('\\addpenalty{-300}%\n') # do break page *before* labels
        self.write_labels (section)

        if short_title and self.toc_depth >= self.section_level:
            self.write_pdf_bookmark (section, short_title)

        self.cmd ('%%\n\\%s*{' % (section_command))
            
    def depart_section_title (self, node):
        self.cmd ('}\n\n')

    def visit_section_subtitle (self, node):
        self.sp (1)
        self.begin ('center')
    
    def depart_section_subtitle (self, node):
        self.end ()
        self.sp (2)

    def visit_topic (self, node):
        self.begin ('quote')

    def depart_topic (self, node):
        self.end ()

    def visit_topic_title (self, node):
        self.cmd ('\\textbf{')

    def depart_topic_title (self, node):
        self.cmd ('}\\par\n\n\\vspace{1em}\n\n')

    def visit_sidebar (self, node):
        pass

    def depart_sidebar (self, node):
        pass

    def visit_rubric (self, node):
        pass

    def depart_rubric (self, node):
        pass

    def visit_page (self, node):
        if 'vspace' in node['classes']:
            self.cmd ('\\vspace{%dem}\n' % node['length'])
        elif 'clearpage' in node['classes']:
            self.cmd ('\\clearpage\n')
        elif 'cleardoublepage' in node['classes']:
            self.cmd ('\\cleardoublepage\n')
        elif 'vfill' in node['classes']:
            self.cmd ('\\vspace*{\\fill}\n')
        else:
            for matter in ('frontmatter', 'mainmatter', 'backmatter'):
                if matter in node['classes']:
                    self.cmd ('\n%%\n\\%s\n%%\n\n' % matter)

    def depart_page (self, node):
        pass
    
    def visit_transition (self, node):
        self.cmd (r'\medskip\noindent\hspace*{\fill}\hrulefill\hspace*{\fill}\par\medskip\noindent' + '\n\n')

    def depart_transition (self, node):
        pass

    def visit_problematic (self, node):
        self.cmd ('nf')

    def depart_problematic (self, node):
        self.cmd ('fi')

    def unimplemented_visit (self, node):
        raise NotImplementedError ('visiting unimplemented node type: %s'
                                  % node.__class__.__name__)
