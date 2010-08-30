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

import sys
import ast
from sexpy.parser import String, List

EXPRESSION_OPERATORS = {}
STATEMENT_OPERATORS = {}

def lineno(obj):
    """Tries to obtain a line number from the code"""

    try:
        return obj.lineno
    except AttributeError:
        return 0

def add_lineno(func):
    """A decorator for code generation functions for automatically adding
    a lineno to the resulting Python AST node
    """
    def new_func(code):
        node = func(code)
        node.lineno = lineno(code)
        node.col_offset = 0 # FIXME
        return node
    return new_func

def expression_operator(operator):
    """A decorator function for registering expression operators"""

    def register(func):
        func = add_lineno(func)
        EXPRESSION_OPERATORS[operator] = func
        return func
    return register

def statement_operator(operator):
    """A decorator function for registering statement operators"""
    def register(func):
        func = add_lineno(func)
        STATEMENT_OPERATORS[operator] = func
        return func
    return register

def make_unary_operator(op_class):
    """Create a function that will create an AST node for an unary operator"""
    @add_lineno
    def func(args):
        return ast.UnaryOp(op_class(), expression(args[1]))
    return func

def make_binary_operator(op_class):
    """Create a function that will create an AST node for a binary operator"""
    @add_lineno
    def func(args):
        left, right = expressions(args[1:])
        return ast.BinOp(left, op_class(), right)
    return func

def make_bool_operator(op_class):
    """Create a function that will create an AST node for a binary operator"""
    @add_lineno
    def func(args):
        values = expressions(args[1:])
        return ast.BoolOp(op_class(), values)
    return func

def make_comparison_operator(op_class):
    """Create a function that will create an AST node for a comparison operator"""
    @add_lineno
    def func(args):
        left, right = expressions(args[1:])
        return ast.Compare(left, [op_class()], [right])
    return func

def make_return_operator(op_class):
    @add_lineno
    def func(code):
        if len(code) == 1: # return
            return op_class()
        elif len(code) == 2: # return <expr>
            return op_class(expression(code[1]))
        else:
            raise SyntaxError
    return func

EXPRESSION_OPERATORS.update(
    (operator, make_binary_operator(node)) for (operator, node) in (
        ('+', ast.Add),
        ('-', ast.Sub),
        ('*', ast.Mult),
        ('/', ast.Div),
        ('//', ast.FloorDiv),
        ('**', ast.Pow),
        ('%', ast.Mod),
        ('|', ast.BitOr),
        ('&', ast.BitAnd),
        ('^', ast.BitXor),
        ))

EXPRESSION_OPERATORS.update(
    (operator, make_bool_operator(node)) for (operator, node) in (
        ('or', ast.Or),
        ('and', ast.And),
        ))

EXPRESSION_OPERATORS.update(
    (operator, make_comparison_operator(node)) for (operator, node) in (
        ('==', ast.Eq),
        ('!=', ast.NotEq),
        ('<', ast.Lt),
        ('<=', ast.LtE),
        ('>', ast.Gt),
        ('>=', ast.GtE),
        ('is', ast.Is),
        ('in', ast.In),
        ))


EXPRESSION_OPERATORS.update(
    (operator, make_unary_operator(node)) for (operator, node) in (
        ('not', ast.Not),
        ('~', ast.Invert),
        ))

STATEMENT_OPERATORS['return'] = make_return_operator(ast.Return)
EXPRESSION_OPERATORS['yield'] = make_return_operator(ast.Yield)


@statement_operator('=')
def assign(code):
    assert len(code) == 3
    lvalue = expression(code[1])
    rvalue = expression(code[2])
    if isinstance(lvalue, (ast.Name, ast.Attribute, ast.Subscript)):
        lvalue.ctx = ast.Store()
        return ast.Assign([lvalue], rvalue)
    elif isinstance(lvalue, ast.List):
        lvalue.ctx = ast.Store()
        for elt in lvalue.elts:
            elt.ctx = ast.Store()
        return ast.Assign([lvalue], rvalue)
    else:
        raise SyntaxError

@expression_operator('.')
def getattr_(args):
    return ast.Attribute(expression(args[1]), str(args[2]), ast.Load())

@expression_operator('..')
def subscript(args):
    # FIXME implement multiple indexes and slices
    return ast.Subscript(expression(args[1]), ast.Index(expression(args[2])), ast.Load())

@statement_operator('class')
def class_(code):
    declaration = code[1]
    name = str(declaration[0])
    bases = expressions(declaration[1:])
    body = statements(code[2:])
    return ast.ClassDef(
        name=name,
        bases=bases,
        keywords=[],
        starargs=None,
        kwargs=None,
        body=body,
        decorator_list=[],
    )

@statement_operator('def')
def def_(code):
    signature = code[1]
    name = str(signature[0])
    arg_list = [ast.arg(str(arg_name), None) for arg_name in signature[1:]]
    args = ast.arguments(
        args=arg_list,
        vararg=None,
        varargannotation=None,
        kwonlyargs=[],
        kwarg=None,
        kwargannotation=None,
        defaults=[],
        kw_defaults=[]
    )
    body = statements(code[2:])
    return ast.FunctionDef(name, args, body, [], None)

@statement_operator('from')
def from_(code):
    assert len(code) >= 3
    if code[2] == 'import':
        names = code[3:]
    else:
        names = code[2:]
    return ast.ImportFrom(str(code[1]), [ast.alias(str(module_name), None) for module_name in names], 0)

@statement_operator('for')
def for_(code):
    assert len(code) >= 3
    target = expression(code[1])
    target.ctx = ast.Store()
    iter = expression(code[2])
    body = statements(code[3:])
    return ast.For(target, iter, body, [])

@statement_operator('if')
def if_(code):
    test = expression(code[1])
    body = statements(code[2])
    if len(code) == 3:
        orelse = []
    elif len(code) == 4:
        orelse = statements(code[3])
    else:
        raise SyntaxError
    return ast.If(test, body, orelse)

@statement_operator('while')
def while_(code):
    test = expression(code[1])
    body = statements(code[1:])
    return ast.While(test=test, body=body, orelse=[])

@statement_operator('import')
def import_(code):
    assert len(code) >= 2
    return ast.Import([ast.alias(str(module_name), None) for module_name in code[1:]])
        
@statement_operator('raise')
def raise_(code):
    assert len(code) == 2
    return ast.Raise(exc=expression(code[1]))

def expressions(code):
    return [expression(e) for e in code]

@add_lineno
def expression(code):
    """Create a Python AST node for an arbitrary SEXpy expression"""
    if isinstance(code, int):
        return ast.Num(int(code))
    elif isinstance(code, String):
        return ast.Str(str(code))
    elif isinstance(code, List):
        return ast.List(expressions(code), ast.Load())
    elif isinstance(code, str):
        return varname(code)
    else:
        try:
            operator = EXPRESSION_OPERATORS[code[0]]
        except (KeyError, TypeError):
            return call(code)
        return operator(code)

def varname(name):
    parts = name.split('.')
    obj = ast.Name(parts[0], ast.Load(), lineno=lineno(name), col_offset=0)
    for attr in parts[1:]:
        obj = ast.Attribute(obj, attr, ast.Load(), lineno=lineno(name), col_offset=0)
    return obj

@add_lineno
def statement(code):
    """Create a Python AST node for an arbitrary SEXpy statement (or expression)"""
    try:
        operator = code[0]
    except:
        return ast.Expr(expression(code))
    try:
        operator = STATEMENT_OPERATORS[operator]
    except (KeyError, TypeError):
        return ast.Expr(expression(code))
    return operator(code)

def statements(code):
    return [statement(i) for i in code]

@add_lineno
def call(code):
    return ast.Call(expression(code[0]), expressions(code[1:]), [], None, None)

def module(code):
    return ast.Module(statements(code))

def interactive(code):
    return ast.Interactive(statements(code))

TRANSLATION_MODES = {
    'exec': module,
    'single': interactive,
}

def to_python_ast(sex_ast, mode='exec'):
    """Create a Python AST from a SEXpy AST"""

    return TRANSLATION_MODES[mode](sex_ast)

def sex_compile(sex_ast, filename='<input>', mode='exec'):
    """Create a Python code object from a SEXpy AST"""

    python_ast = to_python_ast(sex_ast, mode)
    return compile(python_ast, filename, mode)
