###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

from tinypie.lexer import Lexer
from tinypie import tokens
from tinypie.ast import AST
from tinypie.scope import LocalScope
from tinypie.symbol import VariableSymbol, FunctionSymbol

# program             -> (function_definition | statement)+ EOF
# function_definition -> 'def' ID '(' (ID (',' ID)*)? ')' slist
# slist               -> ':' NL statement+ '.' NL
#                        | statement
# statement           -> 'print' expr NL
#                        | 'return' expr NL
#                        | call NL
#                        | assign NL
#                        | 'if' expr slist ('else' slist)?
#                        | 'while' expr slist
#                        | NL
# assign              -> ID '=' expr
# expr                -> add_expr (('<' | '==') add_expr)?
# add_expr            -> mult_expr (('+' | '-') mult_expr)*
# mult_expr           -> atom ('*' atom)*
# atom                -> ID | INT | STRING | call | '(' expr ')'
# call                -> ID '(' (expr (',' expr)*)? ')'


class ParserException(Exception):
    pass


class BaseParser(object):

    # Helper methods
    def _init_lookahead(self):
        for _ in range(self.lookahead_limit):
            self._consume()

    def _match(self, token_type):
        if self._lookahead_type(0) == token_type:
            self._consume()
        else:
            raise ParserException(
                'Expecting %s; found %s' % (
                    token_type, self._lookahead_token(0))
                )

    def _consume(self):
        self.lookahead[self.pos] = self.lexer.token()
        self.pos = (self.pos + 1) % self.lookahead_limit

    def _lookahead_type(self, number):
        return self._lookahead_token(number).type

    def _lookahead_token(self, number):
        return self.lookahead[(self.pos + number) % self.lookahead_limit]


class TACParser(BaseParser):

    def __init__(self, lexer, lookahead_limit=2):
        self.lexer = lexer
        self.lookahead = [None] * lookahead_limit
        self.lookahead_limit = lookahead_limit
        self.pos = 0
        self._init_lookahead()
        self.root = AST(tokens.BLOCK)

    def parse(self):
        node = AST(tokens.BLOCK)

        while self._lookahead_type(0) != tokens.EOF:
            token_type = self._lookahead_type(0)
            if (token_type == tokens.ID
                and self._lookahead_type(1) == tokens.ASSIGN
                ):
                node = self._statement()

        self.root = node

    def _statement(self):
        node = AST(tokens.ASSIGN)
        token = self._lookahead_token(0)
        self._match(tokens.ID)
        self._match(tokens.ASSIGN)
        node.add_child(AST(token))
        expr_node = self._expr()
        node.add_child(expr_node)

        node.code = '\n'.join([expr_node.code,
                               _gen_tac(token.text, '=', expr_node.addr)])

        return node

    def _expr(self):
        node = AST(tokens.ADD)
        left = self._atom()
        self._match(tokens.ADD)
        right = self._atom()
        node.add_child(left)
        node.add_child(right)

        node.addr = _get_temp()
        code = []
        code.append(left.code)
        code.append(right.code)
        code.append(_gen_tac(node.addr, '=', left.addr, '+', right.addr))
        node.code = '\n'.join(code)

        return node

    def _atom(self):
        if self._lookahead_type(0) == tokens.ID:
            token = self._lookahead_token(0)
            node = AST(token)
            self._match(tokens.ID)
            node.code = ''
            node.addr = token.text
            return node


def _gen_tac(*args):
    return ' '.join(args)

_gen = None
def _get_temp():
    global _gen
    _gen = _yield_temp()
    return next(_gen)

def _yield_temp():
    i = 1
    while True:
        yield 't%s' % i
        i += 1

def main():
    import sys
    text = sys.stdin.read()
    #text = 'a = b + c'
    parser = TACParser(Lexer(text))
    parser.parse()
    tree = parser.root
    print tree.to_string_tree()
    print tree.code
