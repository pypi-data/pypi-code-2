#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import os
import os.path
import inspect
import logging

from ply import lex, yacc


class PLYParser(object):
    """Wrapper object for PLY lexer/parser."""

    @classmethod
    def _table_name(cls, suffix, relative=False):
        """Return the module name for PLY's parsetab file."""
        mname = inspect.getmodule(cls).__name__ + '_' + suffix
        if relative:
            mname = mname.split('.')[-1]
        return mname

    @classmethod
    def _write_tables(cls):
        """Write parser table (for distribution purposes)."""
        path = inspect.getfile(cls)
        parent = os.path.split(path)[0]
        # Need to change directories to get the file written at the right
        # location.
        cwd = os.getcwd()
        os.chdir(parent)
        tabname = cls._table_name('lex', relative=True)
        lex.lex(object=cls, lextab=tabname, optimize=True, debug=False)
        tabname = cls._table_name('tab', relative=True)
        yacc.yacc(module=cls, tabmodule=tabname, optimize=True, debug=False)
        os.chdir(cwd)

    def parse(self, input, fname=None, debug=False):
        optimize = not debug
        tabname = self._table_name('lex')
        lexer = lex.lex(object=self, lextab=tabname,
                        optimize=optimize, debug=debug)
        if hasattr(input, 'read'):
            input = input.read()
        lexer.input(input)
        tabname = self._table_name('tab')
        parser = yacc.yacc(module=self, tabmodule=tabname,
                           optimize=optimize, debug=debug)
        if debug:
            logger = logging.getLogger()
        else:
            logger = yacc.NullLogger()
        parsed = parser.parse(lexer=lexer, tracking=True, debug=logger)
        return parsed
