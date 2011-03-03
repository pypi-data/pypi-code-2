# -*- coding: utf-8 -*-

import os
import sys
import textwrap
from docutils.nodes import section
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList, StringList, string2lines
from sphinx.ext.autodoc import prepare_docstring


TABLE_COLS = ['Name', 'Required', 'Searchable', 'Type', 'Storage']

class NotFound(Exception): pass

class IncludeDocDirective(Directive):
    """
    """
    required_arguments = 1
    has_content = False

    def __init__(self,
                 directive,
                 arguments,
                 options,           # ignored
                 content,           # ignored
                 lineno,            # ignored
                 content_offset,    # ignored
                 block_text,        # ignored
                 state,
                 state_machine,     # ignored
                ):
        assert directive == 'includedoc'
        assert len(arguments) == 1
        assert len(arguments[0].split(':')) == 2
        self.module, self.doc = arguments[0].split(':')
        self.state = state
        self.lineno = lineno

    def run(self):

        module = _resolve_dotted_name(self.module)
        if not getattr(module, '__file__', None):
            raise NotFound('No module found for: ' + self.module)

        module_path = os.path.abspath(os.path.dirname(module.__file__))
        doc_path = module_path + self.doc
        
        if not os.path.isfile(doc_path):
            raise NotFound('No doc found for: ' + doc_path)

        result = ViewList()
        result.append(u'', '<includedoc>')
        #for i, line in enumerate(get_doc(what, self.module+':'+self+doc, todoc, options, env)):
        for i, line in enumerate(prepare_docstring(open(doc_path).read())):
            result.append(line, '%s:docstring of %s' % (self.doc, self.module), i)
        result.append(u'', '<includedoc>')

        node = section()
        surrounding_title_styles = self.state.memo.title_styles
        surrounding_section_level = self.state.memo.section_level
        self.state.memo.title_styles = []
        self.state.memo.section_level = 0
        self.state.nested_parse(result, 0, node, match_titles=1)
        self.state.memo.title_styles = surrounding_title_styles
        self.state.memo.section_level = surrounding_section_level

        return node.children

def _resolve_dotted_name(dotted):
    tokens = dotted.split('.')
    path, name = tokens[:-1], tokens[-1]
    thing = __import__('.'.join(path), {}, {}, [str(name)])
    return getattr(thing, name)

def setup(app):
    app.add_directive('includedoc', IncludeDocDirective)
                      
