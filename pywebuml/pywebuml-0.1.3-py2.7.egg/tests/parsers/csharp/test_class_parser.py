# -*- coding: utf-8 -*-

'''
Tests for pywebuml.initialize.parsers.csharp.class_parser:CSharpClassParser

This test will only focus in parsing the class singature. If you want to
see the whole parsing then check test_all_together.py. That module
has test for parsing attribute, class and methods together.
'''

from unittest2 import TestCase

from pywebuml.models import InnerClass
from pywebuml.initialize.parsers.csharp.class_parser import CSharpClassParser

class CSharpClassParserTest(TestCase):

    # TODO: faltan  tests para:
    # cuando tira excepciones...

    def setUp(self):
        self.filepath = './tests/file.cs'
        self.attributes_parsed = 0
        self.methods_parsed = 0
        self.called_partial_class_mock = 0
        self.partial_class_mock = None
        self.parser = CSharpClassParser()
        self.parser.parse_attribute = self.mock_parse_attr
        self.parser.parse_method = self.mock_parse_method
        self.parser.find_partial_class = self.mock_find_partial_class

    def mock_parse_attr(self, content, index, current_class):
        self.attributes_parsed += 1
        return index +1

    def mock_parse_method(self, content, index, current_class):
        self.methods_parsed += 1
        return index +1

    def mock_find_partial_class(self, *args):
        ''' Mocked method for the find partial class of the parser.
        '''
        self.called_partial_class_mock += 1
        if self.called_partial_class_mock > 1:
            return self.partial_class_mock
        return None



    def test_parsing_different_classes(self):
        ''' Test parsing opening and closing { and } positions. '''
        content = [
            "public class Foo1 { };",

            "public class Foo2 {",
            "}",

            "public class Foo3",
            "{",
            "}",
        ]
        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(index, 1)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo1')

        index, klasses = self.parser.parse(self.filepath, content, 1, 'global')
        self.assertEquals(index, 3)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo2')

        index, klasses = self.parser.parse(self.filepath, content, 3, 'global')
        self.assertEquals(index, 6)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo3')

    def test_parse_interface_and_inheritence(self):
        ''' Test what happens when the class extends or implements some
        interfaces.
        '''
        content = [
            "public class Foo : Bar",
            "{",
            "}",

            "public class Foo : Bar1,",
            "Bar2, Bar3",
            "{",
            "}",

            "public class Foo : Bar1,",
            "Bar2, Bar3 {",
            "}",


            "public class Foo : IBar",
            "{",
            "}",

            "public class Foo : IBar1, Bar1,",
            "Bar2, IBar2 {",
            "}",
        ]
        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(index, 3)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo')
        self.assertEquals(len(klass.base_classes), 1)
        self.assertEquals(len(klass.interfaces), 0)
        self.assertEquals(klass.base_classes[0].base_class_package, 'global.Bar')


        index, klasses = self.parser.parse(self.filepath, content,3, 'global')
        self.assertEquals(index, 7)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo')
        self.assertEquals(len(klass.base_classes), 3)
        self.assertEquals(len(klass.interfaces), 0)
        self.assertEquals(klass.base_classes[0].base_class_package, 'global.Bar1')
        self.assertEquals(klass.base_classes[1].base_class_package, 'global.Bar2')
        self.assertEquals(klass.base_classes[2].base_class_package, 'global.Bar3')


        index, klasses = self.parser.parse(self.filepath, content, 7, 'global')
        self.assertEquals(index, 10)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo')
        self.assertEquals(len(klass.base_classes), 3)
        self.assertEquals(len(klass.interfaces), 0)
        self.assertEquals(klass.base_classes[0].base_class_package, 'global.Bar1')
        self.assertEquals(klass.base_classes[1].base_class_package, 'global.Bar2')
        self.assertEquals(klass.base_classes[2].base_class_package, 'global.Bar3')

        index, klasses = self.parser.parse(self.filepath, content, 10, 'global')
        self.assertEquals(index, 13)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo')
        self.assertEquals(len(klass.base_classes), 0)
        self.assertEquals(len(klass.interfaces), 1)
        self.assertEquals(klass.interfaces[0].interface_class_package, 'global.IBar')


        index, klasses = self.parser.parse(self.filepath, content, 13, 'global')
        self.assertEquals(index, 16)
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.name, 'Foo')
        self.assertEquals(len(klass.base_classes), 2)
        self.assertEquals(len(klass.interfaces), 2)
        self.assertEquals(klass.interfaces[0].interface_class_package, 'global.IBar1')
        self.assertEquals(klass.interfaces[1].interface_class_package, 'global.IBar2')
        self.assertEquals(klass.base_classes[0].base_class_package, 'global.Bar1')
        self.assertEquals(klass.base_classes[1].base_class_package, 'global.Bar2')


    def test_check_if_method_or_attribute(self):
        ''' Test to check if a line is a method or attribute. '''
        content = [
            "private int i;",
            "private int i = 3;",
            "private Foo i = new Foo();",
            "private Foo i;",
            "private int bar",
            "private int bar {",
            "public int bar { get { return value; }, set { _bar = value; } };",
            "public int bar { get  { return mVar; } }",
            "public int bar { set { _bar = value: } }",
            "int[] bar",
            "int[] bar = new int[2] { 1, 2}",
            "int[] bar = new int[2] {",
            "Foo[] bar = new Foo[1] { new Foo(1, 2) }",
            "enum BAR {",
            "enum BAR",
            "int i // default Foo()",
            "public Foo()",
            "public void Foo() {",
            "public void Foo()",
            "public void Foo() { foo = 2};",
            "public void Foo() { return 3 };",
            "public void Foo(int bar)",
            "public void Foo(int bar) {",
            "public void Foo(int bar) { foo = 3 };",
            "public int getValue()",
            "public int setValue()",
            "private Dictionary<string, T?> method1() where T : new",
            "public static bool operator !=(Foo lhs, Foo rhs)"
            "public int foo(int j) // default j = 3",

        ]
        for index, current_line in enumerate(content):
            is_method = index >= 16
            self.assertEquals(self.parser.is_method(current_line), is_method, msg=current_line)

    def test_parse_inner_class(self):
        ''' Test parsing some inner classes. '''
        content = [
            "public class Foo",
            "{",
                "private class Inner1 {}",
                "private class Inner2 {",
                "}",
                "private class Inner3",
                "{",
                "}",

                "public struct Inner4",
                "{",
                "}",
            "}",
        ]
        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(index, 12)
        self.assertEquals(len(klasses), 5)
        self.assertEquals(klasses[0].package, 'global.Foo')
        self.assertEquals(len(klasses[0].inner_classes), 4)

        for index, klass in enumerate(klasses[1:]):
            self.assertEquals(klass.package, 'global.Foo.Inner%s' % (index +1))
            self.assertTrue(isinstance(klass, InnerClass))


    def test_oneline_inner_with_extends_classes(self):
        ''' Test parsing inner classes when they extend another class. '''
        content = [
            'public class Foo : Base',
            '{',
                'public new class Inner1 : Base.Inner1 {}',
                'public new class Inner2: Base.Inner2 {}',
            '}',
        ]
        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(index, 5)
        self.assertEquals(len(klasses), 3)
        self.assertEquals(klasses[0].package, 'global.Foo')
        self.assertEquals(klasses[0].base_classes[0].base_class_package, 'global.Base')
        self.assertEquals(len(klasses[0].inner_classes), 2)
        self.assertEquals(klasses[1].package, 'global.Foo.Inner1')
        self.assertEquals(klasses[1].base_classes[0].base_class_package, 'global.Base.Inner1')
        self.assertEquals(klasses[2].package, 'global.Foo.Inner2')
        self.assertEquals(klasses[2].base_classes[0].base_class_package, 'global.Base.Inner2')


    def test_parse_interface(self):
        ''' Test parsing an interface. '''
        content = [
            "public interface Foo1",
            "{",
            "}",

            "public abstract Foo2",
            "{",
            "}",

            "public class Foo3",
            "{",
            "}",
        ]
        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.package, 'global.Foo1')
        self.assertTrue(klass.is_interface)

        index, klasses = self.parser.parse(self.filepath, content, 3, 'global')
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.package, 'global.Foo2')
        self.assertFalse(klass.is_interface)

        index, klasses = self.parser.parse(self.filepath, content, 6, 'global')
        self.assertEquals(len(klasses), 1)
        klass = klasses[0]
        self.assertEquals(klass.package, 'global.Foo3')
        self.assertFalse(klass.is_interface)



    def test_parse_class_with_attr_and_methods(self):
        ''' Test a whole class but with some mocked methods. '''
        content = [
            "public class Foo",
            "{",
                "private int i;",
                "// privte int j;",

                "public Foo() : base() { this.i = 1 }",

                "/*",
                " * private int k = 3",
                " */",

                "private int  l = 2;",

                "/* public Foo(int i) {"
                " * this.i = i;",
                " } */",

            "}",
        ]
        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(len(klasses), 1)

        self.assertEquals(self.methods_parsed, 1)
        self.assertEquals(self.attributes_parsed, 2)


    def test_partial_classes(self):
        ''' Test parsing some partial classes, '''
        content = [
            "public partial class Foo",
            "{",
                "private int i",
                "public Foo() {}",
            "}",

            "public partial class Foo",
            "{",
                "private int j",
                "public Foo(int k) {}",
            "}",
        ]


        index, klasses = self.parser.parse(self.filepath, content, 0, 'global')
        self.assertEquals(len(klasses), 1)
        self.assertEquals(self.called_partial_class_mock, 1)
        self.assertEquals(self.methods_parsed, 1)
        self.assertEquals(self.attributes_parsed, 1)


        self.partial_class_mock =   klasses[0]

        index, klasses = self.parser.parse(self.filepath, content, 5, 'global')
        self.assertEquals(len(klasses), 1)
        self.assertTrue(klasses[0] is self.partial_class_mock)
        self.assertEquals(self.called_partial_class_mock, 2)
        self.assertEquals(self.methods_parsed, 2)
        self.assertEquals(self.attributes_parsed, 2)





