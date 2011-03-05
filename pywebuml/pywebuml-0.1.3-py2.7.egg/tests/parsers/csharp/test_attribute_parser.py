# -*- coding: utf-8 -*-

'''
Test for ``pywebuml.initialize.parsers.csharp.attribute_parser.CSharpAttributeParser
'''

from unittest2 import TestCase
from pywebuml.models import Class
from pywebuml.initialize.parsers.csharp.attribute_parser import CSharpAttributeParser
from pywebuml.initialize.parsers.exceptions import (
                    ClossingArrayException,
                    EmptyNameException
                    )


class CSharpAttributeParserTest(TestCase):



    def setUp(self):
        self.parser = CSharpAttributeParser();
        self.class_model = Class('global', 'Foo', '', False, '', 'C#')


    def test_parse_simple_attributes(self):
        ''' Test parsing some simple attributes. '''
        content = [
            "private int i;",
            "private int j = 3;",
            'private string k = "Helo World";',
            "private string l = null;",
            "string m",
            'private bool? n',
        "}" # this is for the end of the class definition
        ]
        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(attr.name, 'i')
        self.assertEquals(attr.type, 'int')
        self.assertEquals(attr.referenced_class_package, None)

        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'j')
        self.assertEquals(attr.type, 'int')
        self.assertEquals(attr.referenced_class_package, None)

        index, attr = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(attr.name, 'k')
        self.assertEquals(attr.type, 'string')
        self.assertEquals(attr.referenced_class_package, None)

        index, attr = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 4)
        self.assertEquals(attr.name, 'l')
        self.assertEquals(attr.type, 'string')
        self.assertEquals(attr.referenced_class_package, None)

        index, attr = self.parser.parse(self.class_model, content, 4)
        self.assertEquals(index, 5)
        self.assertEquals(attr.name, 'm')
        self.assertEquals(attr.type, 'string')
        self.assertEquals(attr.referenced_class_package, None)

        index, attr = self.parser.parse(self.class_model, content, 5)
        self.assertEquals(index, 6)
        self.assertEquals(attr.name, 'n')
        self.assertEquals(attr.type, 'bool?')
        self.assertEquals(attr.referenced_class_package, None)



    def test_parse_objects(self):
        ''' Test parsing some object values '''
        content = [
            "private Foo foo;",
            "private Bar bar = null;",
            "private FooBar other = new Foo();",
            "private IFoo another = new Foo(1, 2);",
        "}" # this is for the end of the class definition
        ]
        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(attr.name, 'foo')
        self.assertEquals(attr.type, 'Foo')
        self.assertEquals(attr.referenced_class_package, 'global.Foo')

        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'bar')
        self.assertEquals(attr.type, 'Bar')
        self.assertEquals(attr.referenced_class_package, 'global.Bar')

        index, attr = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(attr.name, 'other')
        self.assertEquals(attr.type, 'FooBar')
        self.assertEquals(attr.referenced_class_package, 'global.FooBar')

        index, attr = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 4)
        self.assertEquals(attr.name, 'another')
        self.assertEquals(attr.type, 'IFoo')
        self.assertEquals(attr.referenced_class_package, 'global.IFoo')


    def test_parse_arrays(self):
        ''' Test parsing attributes that are arrays. '''
        content = [
            "private int[] foo;",
            "private int[] i = new int[3];",
            "private int[] j = new int[2] { 1, 2};",
            "private int[] k = new int[2] {",
                "1, 2",
            "}",
            "private int[] l = new int[2] {",
                "1, 2 };",
            "private int[] m = new int[2]",
                "{",
                    "1",
                    "2",
                "};",

            "private int[] n = new int[2]",
                "{ 1,",
                "2 };",

        "}" # this is for the end of the class definition
        ]
        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(attr.name, 'foo')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'i')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(attr.name, 'j')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 6)
        self.assertEquals(attr.name, 'k')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 6)
        self.assertEquals(index, 8)
        self.assertEquals(attr.name, 'l')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 8)
        self.assertEquals(index, 13)
        self.assertEquals(attr.name, 'm')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 13)
        self.assertEquals(index, 16)
        self.assertEquals(attr.name, 'n')
        self.assertEquals(attr.type, 'int[]')
        self.assertTrue(attr.referenced_class_package is None)


    def test_get_documentation(self):
        ''' Test getting the documentation of an attribute '''
        content = [
            "// this is the doc...",
            "private int i = 3;",

            "///",
            "/// this is another doc",
            "///",
            "private int j;",

            "/* short documentation */",
            "private int k = 3;",

            "/**",
            "* Long documentation",
            "* /",
            "private int l;",

            "private int m // this is inlie...",
        "}"
        ]
        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'i')
        self.assertEquals(attr.documentation, 'this is the doc...')

        index, attr = self.parser.parse(self.class_model, content, 5)
        self.assertEquals(index, 6)
        self.assertEquals(attr.name, 'j')
        self.assertEquals(attr.documentation, 'this is another doc')

        index, attr = self.parser.parse(self.class_model, content, 7)
        self.assertEquals(index, 8)
        self.assertEquals(attr.name, 'k')
        self.assertEquals(attr.documentation, 'short documentation')

        index, attr = self.parser.parse(self.class_model, content, 11)
        self.assertEquals(index, 12)
        self.assertEquals(attr.name, 'l')
        self.assertEquals(attr.documentation, 'Long documentation')

        index, attr = self.parser.parse(self.class_model, content, 12)
        self.assertEquals(index, 13)
        self.assertEquals(attr.name, 'm')
        self.assertEquals(attr.documentation, 'this is inlie...')


    def test_parse_attribute_with_spaces(self):
        ''' Test parsing and attribute that has more than 1 space between
        the words.'''
        content = [
            "private     int     i   =   3",
            "private   Foo   j",
        "}",
        ]
        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(attr.name, 'i')
        self.assertEquals(attr.type, 'int')

        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'j')
        self.assertEquals(attr.type, 'Foo')
        self.assertEquals(attr.referenced_class_package, 'global.Foo')

    def test_parse_attribute_with_properties(self):
        ''' Test properties definitions. '''
        content = [
            "private int i { get { return foo; } }",
            "private int j { get { return foo; } set { foo = value; } };",
            "private int k {",
                    "get { return foo; }",
                    "set { foo = value }",
            "}",

            "private int l",
            "{",
                "get { return foo; }",
            "}",

            "public int m { get { return new Foo() } };",
            "public int n",
                "{  get { return new Foo() } };",

            "public int o",
                "{  set { _var = value } };",

            "public int p",
                "{  set { _var = value }, get { return new Foo() } };",
        "}",
        ]
        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(attr.name, 'i')

        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'j')

        index, attr = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 6)
        self.assertEquals(attr.name, 'k')

        index, attr = self.parser.parse(self.class_model, content, 6)
        self.assertEquals(index, 10)
        self.assertEquals(attr.name, 'l')

        index, attr = self.parser.parse(self.class_model, content, 10)
        self.assertEquals(index, 11)
        self.assertEquals(attr.name, 'm')

        index, attr = self.parser.parse(self.class_model, content, 11)
        self.assertEquals(index, 13)
        self.assertEquals(attr.name, 'n')

        index, attr = self.parser.parse(self.class_model, content, 13)
        self.assertEquals(index, 15)
        self.assertEquals(attr.name, 'o')

        index, attr = self.parser.parse(self.class_model, content, 15)
        self.assertEquals(index, 17)
        self.assertEquals(attr.name, 'p')



    def test_final_static(self):
        ''' Test to get if a value is final and static. '''
        content = [
            "private int i = 0",
            "private static string j",
            "private const string k",
            "private static readonly string m",
        ]
        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(attr.name, 'i')
        self.assertEquals(attr.is_final, False)
        self.assertEquals(attr.is_static, False)

        index, attr = self.parser.parse(self.class_model, content, 1)
        self.assertEquals(index, 2)
        self.assertEquals(attr.name, 'j')
        self.assertEquals(attr.is_final, False)
        self.assertEquals(attr.is_static, True)

        index, attr = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(attr.name, 'k')
        self.assertEquals(attr.is_final, True)
        self.assertEquals(attr.is_static, False)

        index, attr = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 4)
        self.assertEquals(attr.name, 'm')
        self.assertEquals(attr.is_final, True)
        self.assertEquals(attr.is_static, True)


    def test_parsing_complex_strutctures(self):
        ''' Test parsing list, dictionaries, enums and '''
        content = [
            "public enum MY_ENUM",
            "{",
                "A",
                "B",
            "}",

            "private List<Bar> i",
            "private Dictionary<string, Val> j",

            "private int [] k",
            "private L L",
            "private List <Foo> m",

            "public int this [int index]",
            "{",
                "get",
                "{",
                    "return myArray[index];",
                "}",
                "set",
                "{",
                    "myArray[index] = value;",
                "}",
            "}",
        "}",
        ]

        index, attr = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 5)
        self.assertEquals(attr.name, 'MY_ENUM')
        self.assertEquals(attr.type, 'enum')

        index, attr = self.parser.parse(self.class_model, content, 5)
        self.assertEquals(index, 6)
        self.assertEquals(attr.name, 'i')
        self.assertEquals(attr.type, 'List<Bar>')
        self.assertEquals(attr.referenced_class_package, 'global.Bar')

        index, attr = self.parser.parse(self.class_model, content, 6)
        self.assertEquals(index, 7)
        self.assertEquals(attr.name, 'j')
        self.assertEquals(attr.type, 'Dictionary<string, Val>')
        self.assertEquals(attr.referenced_class_package, 'global.Val')

        index, attr = self.parser.parse(self.class_model, content, 7)
        self.assertEquals(index, 8)
        self.assertEquals(attr.name, 'k')
        self.assertEquals(attr.type, 'int []')
        self.assertTrue(attr.referenced_class_package is None)

        index, attr = self.parser.parse(self.class_model, content, 8)
        self.assertEquals(index, 9)
        self.assertEquals(attr.name, 'L')
        self.assertEquals(attr.type, 'L')
        self.assertEquals(attr.referenced_class_package, 'global.L')

        index, attr = self.parser.parse(self.class_model, content, 9)
        self.assertEquals(index, 10)
        self.assertEquals(attr.name, 'm')
        self.assertEquals(attr.type, 'List <Foo>')
        self.assertEquals(attr.referenced_class_package, 'global.Foo')

        index, attr = self.parser.parse(self.class_model, content, 10)
        self.assertEquals(index, 21)
        self.assertTrue(attr is None)







    def test_parse_different_errors(self):
        ''' Test parsing different attributes when the file isn't correct.
        '''
        content = [
            "private int[] i = new int[2] {",
                "1,",
                "2",
        ]

        with self.assertRaises(ClossingArrayException) as cm:
            self.parser.parse(self.class_model, content, 0)
            self.assertEquals(cm.expected.line, 0)


        content2 = [
            "THIS_MODIFIER_DOESNT_EXISTS int i = 2",
            "moddifier1 moddifier2 int j = 3",
            "private int",

        ]
        with self.assertRaises(EmptyNameException) as cm:
            self.parser.parse(self.class_model, content2, 0)
            self.assertEquals(cm.expected.line, 0)
            self.assertEquals(cm.name, 'int[] i')


        with self.assertRaises(EmptyNameException) as cm:
            self.parser.parse(self.class_model, content2, 0)
            self.assertEquals(cm.expected.line, 0)
            self.assertEquals(cm.name, 'moddifier2 int[] i')


        with self.assertRaises(EmptyNameException) as cm:
            self.parser.parse(self.class_model, content2, 1)
            self.assertEquals(cm.expected.line, 1)
            self.assertEquals(cm.name, '')


    def test_attribute_value_lines(self):
        ''' Test to take into account that the line of the attr could be in the next line.
        '''
        content = [
            "private int i;",
            "private int j = 3;",
            "private int k =",
                "4;",
            "private int l",
                "= 5;",
        "}"
        ]
        index, attr =  self.parser.parse(self.class_model, content, 0)
        self.assertEquals(attr.name, 'i');
        self.assertEquals(index, 1)

        index, attr =  self.parser.parse(self.class_model, content, 1)
        self.assertEquals(attr.name, 'j');
        self.assertEquals(index, 2)

        index, attr =  self.parser.parse(self.class_model, content, 2)
        self.assertEquals(attr.name, 'k');
        self.assertEquals(index, 4)

        index, attr =  self.parser.parse(self.class_model, content, 4)
        self.assertEquals(attr.name, 'l');
        self.assertEquals(index, 6)







