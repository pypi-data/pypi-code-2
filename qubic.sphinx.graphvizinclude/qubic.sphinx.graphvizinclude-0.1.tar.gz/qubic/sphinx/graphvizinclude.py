# -*- coding: utf-8 -*-
'''
Created on Jun 18, 2010

@author: nlaurance
'''
# -*- coding: utf-8 -*-

from sphinx.util.compat import Directive
from sphinx.ext.graphviz import graphviz
#NIL
import os
import sys
import codecs
from os import path


class GraphvizInclude(Directive):
    """
    Directive to insert arbitrary dot markup from external dot resource
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        node = graphviz()

        document = self.state.document
        filename = self.arguments[0]
        if not document.settings.file_insertion_enabled:
            return [document.reporter.warning('File insertion disabled',
                                              line=self.lineno)]
        env = document.settings.env
        if filename.startswith('/') or filename.startswith(os.sep):
            rel_fn = filename[1:]
        else:
            docdir = path.dirname(env.doc2path(env.docname, base=None))
            rel_fn = path.normpath(path.join(docdir, filename))
        try:
            fn = path.join(env.srcdir, rel_fn)
        except UnicodeDecodeError:
            # the source directory is a bytestring with non-ASCII characters;
            # let's try to encode the rel_fn in the file system encoding
            rel_fn = rel_fn.encode(sys.getfilesystemencoding())
            fn = path.join(env.srcdir, rel_fn)

        encoding = self.options.get('encoding', env.config.source_encoding)
        codec_info = codecs.lookup(encoding)
        try:
            f = codecs.StreamReaderWriter(open(fn, 'U'),
                    codec_info.streamreader, codec_info.streamwriter, 'strict')
            lines = f.readlines()
            f.close()
        except (IOError, OSError):
            return [document.reporter.warning(
                'Include file %r not found or reading it failed' % filename,
                line=self.lineno)]
        except UnicodeError:
            return [document.reporter.warning(
                'Encoding %r used for reading included file %r seems to '
                'be wrong, try giving an :encoding: option' %
                (encoding, filename))]

        text = ''.join(lines)
        document.settings.env.note_dependency(rel_fn)

        node['code'] = text
        node['options'] = []
        return [node]


def setup(app):
    app.add_directive('graphvizinclude', GraphvizInclude)
