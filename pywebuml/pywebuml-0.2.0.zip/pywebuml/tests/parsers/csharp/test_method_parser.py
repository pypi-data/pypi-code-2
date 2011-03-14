# -*- coding: utf-8 -*-

'''
Tests for pywebuml.initialize.parsers.csharp.method_parser:CSharpMethodParser
'''

from unittest2 import TestCase
from pywebuml.models import Class, Abstract, Interface
from pywebuml.initialize.parsers.csharp.method_parser import CSharpMethodParser

class MethodParserTest(TestCase):

    # TODO: falta:
    # - agregar los tests para validar el tema de las excepciones...

    def setUp(self):
        self.parser = CSharpMethodParser();
        self.class_model = Class('global', 'Foo', './foo.cs', 'C#')

    def test_different_openings_and_closing(self):
        ''' Test different position for { and } '''
        content = [
            "public void foo() { doSomething(); }",
            "public void foo() {",
                "doSomething()",
            "}",
            "public void foo()",
            "{",
                "doSomething()",
            "}",
        "}"
        ]
        index, method = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo()')


        index, method = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 4)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo()')

        index, method = self.parser.parse(self.class_model, content, 4)
        self.assertEquals(index, 8)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo()')

    def test_parse_different_signatures(self):
        ''' Test parsing different signatures. '''
        content = [
            "public void foo() { doSomething() }",
            "public void foo(int bar) { doSomething() }",
            "public int foo() { doSomething() }",
            "public int foo(int bar) { doSomething() }",

            "public int foo(int bar, int[] other)",
            "{",
                "doSomething()",
            "}",

            "public void foo(T bar) where T : new",
            "{",
                "doSomething()",
            "}",

            "public T foo(int bar) where T : new",
            "{",
                "doSomething()",
            "}",

            "public     int     foo(int   bar,  List  other)",
            "{",
                "doSomething()",
            "}",

        "}"
        ]
        index, method = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo()')

        index, method = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo(int bar)')

        index, method = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'int foo()')

        index, method = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 4)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'int foo(int bar)')


        index, method = self.parser.parse(self.class_model, content, 4)
        self.assertEquals(index, 8)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'int foo(int bar, int[] other)')

        index, method = self.parser.parse(self.class_model, content, 8)
        self.assertEquals(index, 12)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo(T bar)')

        index, method = self.parser.parse(self.class_model, content, 12)
        self.assertEquals(index, 16)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'T foo(int bar)')

        index, method = self.parser.parse(self.class_model, content, 16)
        self.assertEquals(index, 20)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'int foo(int bar, List other)')



    def test_parse_constructors(self):
        ''' Test parsing class constructors '''
        content = [
            "public Foo() : base(3)",
            "{",
                "doSomething()",
            "}",


            "public Foo() :",
                "base(3)",
            "{",
                "doSomething()",
            "}",

            "public Foo() : base(3) {",
                "doSomething()",
            "}",

            "public Foo(int bar) : base(bar) { }",
        "}"
        ]
        index, method = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 4)
        self.assertEquals(method.name, 'Foo')
        self.assertEquals(method.signature, 'Foo()')

        index, method = self.parser.parse(self.class_model, content, 4)
        self.assertEquals(index, 9)
        self.assertEquals(method.name, 'Foo')
        self.assertEquals(method.signature, 'Foo()')

        index, method = self.parser.parse(self.class_model, content, 9)
        self.assertEquals(index, 12)
        self.assertEquals(method.name, 'Foo')
        self.assertEquals(method.signature, 'Foo()')


        index, method = self.parser.parse(self.class_model, content, 12)
        self.assertEquals(index, 13)
        self.assertEquals(method.name, 'Foo')
        self.assertEquals(method.signature, 'Foo(int bar)')


    def test_parse_generics(self):
        ''' Test parsing methods that  have generics. '''
        content = [
            "public Dictionary<int, string> foo() { doSometing(); }",
            "public void foo(Dictionary<int, string> bar) { doSomething(); }",
            "private List<int> foo(Dictionary<int, string> bar) { doSomething(); }",
            "private List<int> foo(Dictionary<int, string> bar, string[] other) { doSomething(); }",
        "}",
        ]
        index, method = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'Dictionary<int, string> foo()')

        index, method = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'void foo(Dictionary<int, string> bar)')

        index, method = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'List<int> foo(Dictionary<int, string> bar)')

        index, method = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 4)
        self.assertEquals(method.name, 'foo')
        self.assertEquals(method.signature, 'List<int> foo(Dictionary<int, string> bar, string[] other)')


    def test_parse_different_methods(self):
        ''' Test parsing different methods... '''
        content = [
            "public void foo(int bar1) { doSomething() }",
            "public void foo(int bar2) {",
                "if (condition) {",
                    "doSomething();",
                "}",
            "}",

            "public void foo(int bar3) {",
                "if (condition)",
                    "doSomething()",
            "}",

            "public void foo(int bar4) {",
                "while (condition)",
                "{",
                    "doSomething();",
                "}",
            "}",




            "public static bool operator !=(Foo foo1, Foo foo2)",
            "{",
                "return foo1.name != foo2.name",
            "}",
        "}"
        ]

        index, method = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.signature, 'void foo(int bar1)')

        index, method = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 6)
        self.assertEquals(method.signature, 'void foo(int bar2)')

        index, method = self.parser.parse(self.class_model, content, 6)
        self.assertEquals(index, 10)
        self.assertEquals(method.signature, 'void foo(int bar3)')

        index, method = self.parser.parse(self.class_model, content, 10)
        self.assertEquals(index, 16)
        self.assertEquals(method.signature, 'void foo(int bar4)')

        index, method = self.parser.parse(self.class_model, content, 16)
        self.assertEquals(index, 20)
        self.assertTrue(method is None)


    def test_parse_abstract_class(self):
        ''' Test parsing methods for a class that is abstract. '''
        content = [
            "public abstract int foo(int k)",

            "public int bar(int i) {",
                "return i;",
            "}",
        "}",
        ]
        class_model = Abstract('global.Foo', 'Foo', './foo.cs', 'C#')

        index, method = self.parser.parse(class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.signature, 'int foo(int k)')
        self.assertTrue(method.is_abstract)

        index, method = self.parser.parse(class_model, content, 1)
        self.assertEquals(index, 4)
        self.assertEquals(method.signature, 'int bar(int i)')
        self.assertFalse(method.is_abstract)

    def test_parse_interface_class(self):
        ''' Test parsing methods for a class that is abstract. '''
        content = [
            "public int foo(int k)",

            "public int bar(int i)",
        "}",
        ]
        class_model = Interface('global.Foo', 'Foo', './foo.cs', 'C#')

        index, method = self.parser.parse(class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.signature, 'int foo(int k)')
        self.assertTrue(method.is_abstract)

        index, method = self.parser.parse(class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(method.signature, 'int bar(int i)')
        self.assertTrue(method.is_abstract)


