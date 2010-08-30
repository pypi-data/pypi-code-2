# Copyright 2007 Ero-sennin
#
# This file is part of SEXpy.
#
# SEXpy is free software; you can redistribute it and/or modify
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# SEXpy is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybtex; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

import shlex

class ImmutableSource(object):
    def __new__(cls, value, lineno):
        instance = super().__new__(cls, value)
        instance.lineno = lineno
        return instance

class Source(object):
    def __init__(self, l, lineno):
        super().__init__(l)
        self.lineno = lineno

class String(ImmutableSource, str):
    """A string literal"""
    def __repr__(self):
        return '"{0}"'.format(self)

class Atom(ImmutableSource, str):
    """An atom"""
    def __repr__(self):
        return str(self)

class Int(ImmutableSource, int):
    """An integer literal"""

class Float(ImmutableSource, float):
    """A floating point literal"""

class SourceList(Source, list):
    """A list that knows its source line number"""
    def __repr__(self):
        return '({0})'.format(' '.join(repr(item) for item in self))

class List(Source, list):
    """A list literal"""
    def __repr__(self):
        return '#({0})'.format(' '.join(repr(item) for item in self))


class SexpSyntaxError(SyntaxError):
    pass

class Parser(object):
    """ S-expression parser

    inspired by the readlisp module by Ole Martin Bjorndalen
    (http://www.cs.uit.no/~olemb/)
    """

    def __init__(self, file, filename=None):
        self.lex = shlex.shlex(file, filename)
        self.lex.commenters = ';'
        self.lex.wordchars = self.lex.wordchars + '![]#|^&.e+-*/_=<>'

    def parse(self, toplevel=False):
        for token in self.lex:
            if token == '(':
                yield SourceList(self.parse(), self.lex.lineno)
            elif token == '#':
                if next(self.lex) != '(':
                    raise SexpSyntaxError(self.lex.error_leader() + 'opening parenthesis expexted')
                yield List(self.parse(), self.lex.lineno)
            elif token == ')':
                if toplevel:
                    raise SexpSyntaxError(self.lex.error_leader() + 'unexpected closing parenthesis')
                return
            else:
                yield self.atom(token)
        if not toplevel:
            raise SexpSyntaxError(self.lex.error_leader() + 'missing closing parenthesis')

    def atom(self, token):
        if token.startswith('"') or token.startswith("'"):
            return String(token[1:-1], self.lex.lineno)
        else:
            for convert in (Int, Float):
                try:
                    return convert(token, self.lex.lineno)
                except ValueError:
                    pass
            return Atom(token, self.lex.lineno)

def parse(instream, filename="<input>"):
    return Parser(instream, filename).parse(toplevel=True)
