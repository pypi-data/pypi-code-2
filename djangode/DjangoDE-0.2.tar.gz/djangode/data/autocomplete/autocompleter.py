# DjangoDE, an integrated development environment for Django
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
import glob
import logging
import os
import sys

from djangode.data.autocomplete.builtins import builtins
from djangode.data.autocomplete._class import Class
from djangode.data.autocomplete.function import Function
from djangode.data.autocomplete.value import Value
from djangode.data.autocomplete.variable import Variable

from djangode import global_objects

logger = logging.getLogger("djangode.data.autocompleter.AutoCompleter")

class AutoCompleter(object):
    def process(self, text):
        return process_text(text)

    def get_top_level_modules(self):
        modules = []

        pythonpath = global_objects.project.get_pythonpath() if global_objects.project is not None else sys.path
        for directory in pythonpath:
            for filename in glob.glob(directory + os.sep + "*"):
                if filename.endswith(".py"):
                    modules.append(filename.split(os.sep)[-1][:-3])
                elif os.path.isdir(filename) and os.path.exists(filename + os.sep + "__init__.py"):
                    modules.append(filename.split(os.sep)[-1])
        return sorted(modules)

    def get_module(self, module_name):
        pythonpath = global_objects.project.get_pythonpath() if global_objects.project is not None else sys.path
        for directory in pythonpath:
            for filename in glob.glob(directory + os.sep + "*"):
                if filename.endswith(".py"):
                    if filename.split(os.sep)[-1][:-3] == module_name:
                        return Module.load_from_file(filename)
                elif os.path.isdir(filename) and os.path.exists(filename + os.sep + "__init__.py"):
                    if filename.split(os.sep)[-1] == module_name:
                        return Module.load_from_file(filename + os.sep + "__init__.py")

def process_text(text):
    tree = None
    while text != "":
        try:
            tree = compiler.parse(text)
        except SyntaxError, e:
            lines = text.split("\n")
            del lines[e.lineno-1]
            text = "\n".join(lines)
        else:
            break

    module = Module()
    module.text_finder = TextFinder(text)
    if tree is not None:
        module.docstring = tree.doc

        process_stmts(module, module.text_finder, tree.node)
    else:
        module.docstring = ""

    return module

def process_stmts(scope, text_finder, stmts):
    for stmt in stmts:
        if isinstance(stmt, compiler.ast.Assign):
            value = process_expr(scope, text_finder, stmt.expr, find_text=False)
            if value is None:
                logger.error("Failed to get value from %s." % (stmt.expr, ))
                continue
            for assign_target in stmt.nodes:
                process_assign(scope, text_finder, assign_target, value)

            tl = process_expr(scope, text_finder, stmt.expr, find_text=True)
            if tl is not None:
                tl.obj = value
        elif isinstance(stmt, compiler.ast.Class):
            c = Class(scope, stmt.name)
            text_finder.find_text(stmt.name, c)
            process_stmts(c, text_finder, stmt.code)
            scope.set_variable(stmt.name, c)
        elif isinstance(stmt, compiler.ast.Discard):
            process_expr(scope, text_finder, stmt.expr, find_text=False)
            process_expr(scope, text_finder, stmt.expr, find_text=True)
        elif isinstance(stmt, compiler.ast.Function):
            func = Function(scope, stmt.name)
            func.tl = text_finder.find_text(stmt.name, func)

            scope.set_variable(stmt.name, Value(func))
        elif isinstance(stmt, compiler.ast.Import):
            for (name, alias) in stmt.names:
                module = AutoCompleter().get_module(name.split(".")[0])
                if module is None:
                    logger.warning("Couldn't find module %s." % (name, ))
                    continue
                text_finder.find_text(name, module)

                scope.set_variable(alias if alias is not None else name, Value(module))
        else:
            logger.error("Unknown Statement %s." % (stmt, ))

def process_expr(scope, text_finder, expr, find_text):
    if isinstance(expr, compiler.ast.CallFunc):
        process_expr(scope, text_finder, expr.node, find_text=True)
        func = process_expr(scope, text_finder, expr.node, find_text=False)
        if func is None:
            return None
        else:
            return func.value.call()
    elif isinstance(expr, compiler.ast.Const):
        if find_text:
            return text_finder.find_text(expr.value, None)
        else:
            _class = builtins.get_variable(type(expr.value).__name__).value

            return Value(_class.call())
    elif isinstance(expr, compiler.ast.Name):
        try:
            if find_text:
                return text_finder.find_text(expr.name, scope.get_variable(expr.name))
            else:
                return scope.get_variable(expr.name)
        except KeyError:
            logger.warning("Couldn't find variable %s." % (expr.name, ))
            return None
    elif isinstance(expr, compiler.ast.Tuple):
            _class = builtins.get_variable("tuple").value

            return Value(_class.call())
    else:
        logger.error("Unknown Expression %s." % (expr, ))

def process_assign(scope, text_finder, assign, value):
    if isinstance(assign, compiler.ast.AssName):
        obj = scope.set_variable(assign.name, value)

        tl = text_finder.find_text(assign.name, None)
        if tl is not None:
            tl.obj = obj
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

from djangode.data.autocomplete.module import Module
