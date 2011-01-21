# DjangoDE, a integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import compiler
import logging

from djangode.data.autocomplete.builtins import builtins
from djangode.data.autocomplete.module import Module
from djangode.data.autocomplete.value import Value
from djangode.data.autocomplete.variable import Variable

logger = logging.getLogger("djangode.data.autocompleter.AutoCompleter")

class AutoCompleter(object):
    def process(self, text):
        try:
            tree = compiler.parse(text)
        except SyntaxError, e:
            logger.warn(unicode(e))
            return

        module = Module()
        module.docstring = tree.doc
        module.text_finder = TextFinder(text)

        self.process_stmts(module, module.text_finder, tree.node)

        return module

    def process_stmts(self, scope, text_finder, stmts):
        for stmt in stmts:
            logger.info(stmt)

            if isinstance(stmt, compiler.ast.Assign):
                value = self.process_expr(scope, text_finder, stmt.expr, find_text=False)
                for assign_target in stmt.nodes:
                    self.process_assign(scope, text_finder, assign_target, value)

                tl = self.process_expr(scope, text_finder, stmt.expr, find_text=True)
                if tl is not None:
                    tl.obj = value
            elif isinstance(stmt, compiler.ast.Discard):
                self.process_expr(scope, text_finder, stmt.expr, find_text=False)
                self.process_expr(scope, text_finder, stmt.expr, find_text=True)
            else:
                logger.error("Unknown Statement %s." % (stmt, ))

    def process_expr(self, scope, text_finder, expr, find_text):
        logger.info(expr)
        if isinstance(expr, compiler.ast.Const):
            if find_text:
                return text_finder.find_text(expr.value, None)
            else:
                _class = builtins.get_variable(type(expr.value).__name__)

                return Value(_class.get_instance())
        elif isinstance(expr, compiler.ast.Name):
            if find_text:
                return text_finder.find_text(expr.name, scope.get_variable(expr.name))
            else:
                return scope.get_variable(expr.name)
        else:
            logger.error("Unknown Expression %s." % (expr, ))

    def process_assign(self, scope, text_finder, assign, value):
        logger.info(assign)
        logger.info(value)

        if isinstance(assign, compiler.ast.AssName):
            tl = text_finder.find_text(assign.name, None)

            tl.obj = scope.set_variable(assign.name, value)
        else:
            logger.error("Unknown Assignment Type %s." % (assign, ))

class TextFinder(object):
    def __init__(self, text):
        self.text = text
        self.text_locations = []
        self.lineno, self.charno = 0, 0

    def find_text(self, needle, obj):
        needle = unicode(needle)

        start = self.text.find(needle)
        if start == -1:
            return

        pre_text, self.text = self.text[:start], self.text[start + len(needle):]
        lines = len(pre_text.split("\n")) - 1
        self.lineno += lines
        if lines > 0:
            self.charno = len(pre_text.split("\n")[-1])
        else:
            self.charno += len(pre_text)

        tl = TextLocation(self.lineno, self.charno, len(needle), obj)
        self.text_locations.append(tl)

        self.charno += len(needle)

        return tl

    def get_at_text_pos(self, lineno, charno):
        for tl in self.text_locations:
           if tl.is_at_text_pos(lineno, charno):
               return tl.obj

class TextLocation(object):
    def __init__(self, lineno, charno, length, obj):
        self.lineno, self.charno, self.length, self.obj = lineno, charno, length, obj

    def is_at_text_pos(self, lineno, charno):
        return self.lineno == lineno and self.charno <= charno and charno <= self.charno + self.length

    def __repr__(self):
        return "<TextLocation %s %s %s %s>" % (self.lineno, self.charno, self.length, self.obj)
