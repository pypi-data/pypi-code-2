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
        self.filepath = './test/foo.c_sharp'
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
