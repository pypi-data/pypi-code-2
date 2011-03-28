#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2011 Volvox Development Team
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
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

import os
import sys
import unittest
import pyctpp2

class TestPyCTPP2(unittest.TestCase):
    def setUp(self):
        self.t = pyctpp2.Engine()
        self.t.path = [os.path.join(os.path.dirname(__file__), 'data')]

    def test_parse(self):
        template = self.t.parse('hello.tmpl')
        template.save_bytecode('hello.ct2')

        template = self.t.load_bytecode('hello.ct2')
        result = template.render(world={ 'name' : 'beautiful World' })
        self.failUnless(result == 'Hello, beautiful World!\n\n')

        result = template.render()
        self.failUnless(result == 'Hello, !\n\n')

        result = template.render(world={ 'name' : 'awfull World' })
        self.failUnless(result == 'Hello, awfull World!\n\n')

    def test_parse_with_object(self):
        class Foo(object):
            def __init__(self):
                self.var = 'bar'

        template = self.t.parse_text('Foo: <TMPL_var foo.var>')

        result = template.render(foo=Foo())
        self.failUnless(result == 'Foo: bar')

    def test_parse_math_expression(self):
        template = self.t.parse('math_expr.tmpl')

        result = template.render(a=2, b=3, age=31)
        self.failUnless(result == '  (2 + 3) / 5 = 1\n  Age correct\n')

    def test_parse_with_syntax_error(self):
        self.failUnlessRaises(SystemError, self.t.parse,
                "syntax-error.tmpl")

    def test_parse_with_io_error(self):
        template = self.t.parse('io-error.tmpl')
        self.failUnlessRaises(IOError, template.render)


    def test_parse_with_none(self):
        template = self.t.parse('hello.tmpl')

        result = template.render(world={ 'name' : None })
        self.failUnless(result == 'Hello, !\n\n')

    def test_parse_text(self):
        template = self.t.parse_text('Foo: <TMPL_var foo>')

        result = template.render(foo='bar')
        self.failUnless(result == 'Foo: bar')


if __name__ == '__main__':
    unittest.main()

