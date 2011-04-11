"""
Build a SQL query dynamically.

The idea behind this module is simple. When we iterate over a Table
instance::

    >>> table = Table(conn, "my table")
    >>> for row in (r for r in table if r.foo == 'bar'):
    ...     print row

First the ``__iter__`` method in the Table is called, which calls
``get_condition`` in this module. The ``get_condition`` function
goes back to the original stack::

    >>> frame = sys._getframe(2)

All we have to do is get the corresponding source code and scope::

    >>> scope = frame.f_globals
    >>> src = inspect.getframeinfo(frame)[3]

But first we need to clean the source a little bit::

    >>> src = src[0].strip()
    >>> if src.endswith(':'): src = '%s pass' % src

This is because the source can be an incomplete line, like::

    for row in (r for r in table if r.foo == 'bar'):

The source is converted to an AST, and parsed with a visitor. There's
one tricky thing the visitor must do: when it gets to the ``for r
in table`` part of the generator expression it must fix the scope
to::

    >>> scope['r'] = table

Because later it will need to evaluate ``r.foo`` (or ``r['foo']``)
as ``table.foo`` when it gets to the comparison ``r.foo == bar``.
Here, ``bar`` is evaluated to itself (a string), and since ``r.foo``
evaluates to an object with the attribute ``_simpleql_id`` it is
replaced by the column name (simply ``foo``). The visitor will then
create a query with the tokens ``foo``, ``==`` and ``bar``, from
which it's trivial to build ``foo="bar"``.
"""

import sys
import inspect
import compiler
import re


def escape(s):
    """
    Escape a string.
    """
    s = s.replace(r'\\', r'\\\\')
    s = s.replace(r'"', r'\"')
    s = '"%s"' % s

    return s


def encode_atom(atom):
    """
    Encode atom.
    """
    return {basestring: lambda s: escape(s),
            unicode   : lambda s: escape(s),
            str       : lambda s: escape(s),
            float     : lambda f: '%.6g' % f,
            long      : lambda f: '%.6g' % f,
            int       : lambda i: repr(i),
           }.get(type(atom), lambda obj: '%s' % obj)(atom)


class ASTVisitor(compiler.visitor.ASTVisitor):
    def __init__(self, scope, table):
        compiler.visitor.ASTVisitor.__init__(self)
        self.scope = scope
        self.table = table

        self.condition = []

    def visitGenExprFor(self, node):
        # Check if we're iterating over the table.
        if self.eval(node.iter) == self.table:
            # Add table with assigned name to the scope.
            self.scope[node.assign.name] = self.table

        # Carry on.
        self.visit(node.assign)
        self.visit(node.iter)
        for if_ in node.ifs: 
            self.visit(if_)
            
    def visitListCompFor(self, node):
        # Check if we're iterating over the table.
        if self.eval(node.list) == self.table:
            # Add table with assigned name to the scope.
            self.scope[node.assign.name] = self.table

        # Carry on.
        self.visit(node.assign)
        self.visit(node.list)
        for if_ in node.ifs: 
            self.visit(if_)

    def visitCompare(self, node):
        """
        Compare values.

        We need to eval the two values and check if any of them is
        a column from the table.
        """
        # Convert multiple comparisons like 1 < a < 2 to
        # (1 < a) and (a < 2).
        if len(node.ops) > 1:
            left = node.expr
            out = []
            for op in node.ops:
                out.append(compiler.ast.Compare(left, [op]))
                left = op[1]
            new_node = compiler.ast.And(out)
            self.visit(new_node)
        
        else:
            # Simple comparison.
            a, op, b = node.getChildren()
            ops = ['<', '>', '==', '!=', '<=', '>=']
            if op in ops:
                a = self.eval(a)
                b = self.eval(b)
            
                # If the objects have an '_simpleql_id' attribute we use it
                # instead. 
                if hasattr(a, '_simpleql_id'): a = a._simpleql_id
                else: a = encode_atom(a)
                self.condition.append(a)

                if op == '==': op = '='
                self.condition.append(op)
                
                if hasattr(b, '_simpleql_id'): b = b._simpleql_id
                else: b = encode_atom(b)
                self.condition.append(b)

    def visitAnd(self, node):
        """
        Join queries with AND.
        """
        self.condition.append("(")
        first = True
        for child in node.nodes:
            if first: first = False
            else: self.condition.append(") AND (")
            self.visit(child)
        self.condition.append(")")

    def visitOr(self, node):
        """
        Join queries with OR.
        """
        self.condition.append("(")
        first = True
        for child in node.nodes:
            if first: first = False
            else: self.condition.append(") OR (")
            self.visit(child)
        self.condition.append(")")

    def visitCallFunc(self, node):
        """
        Return regular expression query if function is re.search.
        """
        if self.eval(node.node) == re.search:
            b, a = node.args
            a = self.eval(a)
            b = self.eval(b)
            
            # If the objects have an '_simpleql_id' attribute we use it
            # instead. 
            if hasattr(a, '_simpleql_id'): a = a._simpleql_id
            else: a = encode_atom(a)
            self.condition.append(a)

            self.condition.append(" LIKE ")
                
            if hasattr(b, '_simpleql_id'): b = b._simpleql_id
            else: b = encode_atom("%%%s%%" % b)
            self.condition.append(b)

    def eval(self, node):
        """
        Eval node.

        This is done by converting the node to bytecode and
        eval()ing the bytecode in the instance scope.
        """
        ast = compiler.ast.Expression(node)
        ast.filename = 'dummy'
        c = compiler.pycodegen.ExpressionCodeGenerator(ast)
        obj = eval(c.getCode(), self.scope)

        return obj


def get_condition(table):
    # We need to get the stack where the table is being iterated.
    # This is called from genexp --> __iter__ --> get_condition, 
    # so we go up 2 frames in the stack.
    frame = sys._getframe(2)

    # Inspect frame.
    fname, lineno, func, src, index = inspect.getframeinfo(frame)
    scope = frame.f_globals
    
    # Fix src.
    if src:
        src = src[0].strip()
        if src.endswith(':'): src = '%s pass' % src  # hack hack hack

    visitor = ASTVisitor(scope, table)
    try:
        ast = compiler.parse(src)
        compiler.walk(ast, visitor)
    except:
        pass

    # Build condition.
    condition = visitor.condition
    if condition:
        condition.insert(0, " WHERE ")
    condition = ''.join(condition)

    return condition
