# -*- coding: utf-8 -*-

'''
Tests for pywebuml.initialize.parsers.csharp.file_parser:CSharpFileParser

As with the class parser test, this test won't have tests for parsing a whole
file. This class will only test the generic file parsing and won't test the
parsing of a class.
'''

from unittest2 import TestCase
from pywebuml.initialize.parsers.csharp.file_parser import CSharpFileParser

class CSharpFileParserTest(TestCase):
    ''' Some basic tests for the file parsing.
    '''
    # TODO:
    # Agregar tests cuando antes de un archivo hay funciones o methodos definidos.

    def mock_class_parsing(self, filepath, content, index, current_namespace, res):
        ''' Mock so that it doesn't parse a class. '''
        self.classes_found += 1
        self.found_namespaces.append(current_namespace)
        return index + 1


    def setUp(self):
        self.classes_found = 0
        self.filepath = './test/foo.cs'
        self.found_namespaces = []
        self.parser = CSharpFileParser()
        self.parser.parse_class_definition = self.mock_class_parsing



    def test_parse_simple_file(self):
        ''' Test parsing a simple file. '''
        content = [
            "public class Foo { }"
        ]
        self.parser.parse_content(self.filepath, content)
        self.assertEquals(self.classes_found, 1)
        self.assertEquals(self.found_namespaces, ['global'])

    def test_parse_with_namespace(self):
        ''' Test parsing a file that has a namespace. '''
        content = [
            "public class Bar {}",
            "namespace foo1 {",
               "public class Bar {}",
            "}",

            "namespace foo2",
            "{",
                "public class Bar {}",
            "}",

            "public class Bar {}",
        ]
        self.parser.parse_content(self.filepath, content)
        self.assertEquals(self.classes_found, 4)
        self.assertEquals(self.found_namespaces, ['global', 'foo1', 'foo2', 'global'])

    def test_parser_documented_file(self):
        ''' Test a file that has some documentation strings. '''
        content = [
            "// Here goes the GLP licence.",
            "namespace foo {",
                "/*",
                "* public class Foo {",
                "* }",
                "* /",

                "// public class Foo {}"
            "}"
        ]
        self.parser.parse_content(self.filepath, content)
        self.assertEquals(self.classes_found, 0)
        self.assertEquals(self.found_namespaces, [])

    def test_parse_simple_precompiler_directive(self):
        ''' Test what happens when the file has a simple compiler directive.
        '''
        content = [
            "#define FOO",
            "#if FOO",
                "public class Bar {}",
            "#endif",
        ]
        expected = [
            "public class Bar {}",
        ]
        actual = self.parser.remove_preprocessor_code(content)
        self.assertEquals(actual, expected)

    def test_parse_if_else_precompiler_directives(self):
        ''' Checks what happens when the file has an #if, #else and #endif.
        '''
        content = [
            "#define FOO",
            "#if FOO",
                "public class Bar {",
            "#else",
                "public class Foo {",
            "#endif",

            "}",
        ]
        expected = [
            'public class Bar {',
            '}'
        ]
        actual = self.parser.remove_preprocessor_code(content)
        self.assertEquals(actual, expected)

    def test_complicated_preprocessor_ifs(self):
        ''' Test what happens if there are some #if, #elif, #else
        '''
        content = [
            '#define FOO',
            '#define BAR',
            '#if PEPE',
                'public class Bar1 {}',
            '#elif PEPE2',
                'public class Bar2 {}',
            '#else',
                'public class Bar3 {}',
            '#endif',
        ]
        expected = [
            'public class Bar3 {}',
        ]
        actual = self.parser.remove_preprocessor_code(content)
        self.assertEquals(actual, expected)

    def test_nested_ifs(self):
        ''' Test what happens with nested ifs.
        '''
        content = [
            '#define FOO',
            '#define BAR',

            '#if PEPE',
                '#if FOO',
                    'LINE 1',
                '#endif',
                'LINE 2',

            '#else',
                '#if FOO',
                    '#undef BAR',
                    '#if BAR',
                        'LINE 3',
                    '#endif',
                    'LINE 4',
                '#endif',
            '#endif',
        ]
        expected = [
            'LINE 4',
        ]
        actual = self.parser.remove_preprocessor_code(content)
        self.assertEquals(actual, expected)

    def test_other_preprocessors_directives(self):
        ''' Test that it also removes the other preprocessor directives.
        '''
        content = [
            '#define FOO',
            '#if FOO',
                '#warning DEBUG is defined',
                '#region BAR',
                    'public class Bar {}',
                '#endregion',
            '#endif',

            '#error This is an error',
        ]
        expected = [
            'public class Bar {}',
        ]
        actual = self.parser.remove_preprocessor_code(content)
        self.assertEquals(actual, expected)

