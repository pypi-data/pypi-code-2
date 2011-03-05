# -*- coding: utf-8 -*-

'''
Tests for pywebuml.initialize.parsers.csharp.method_parser:CSharpMethodParser
'''

from unittest2 import TestCase
from pywebuml.models import Class
from pywebuml.initialize.parsers.csharp.method_parser import CSharpMethodParser

class MethodParserTest(TestCase):

    # TODO: falta:
    # - agregar los tests para validar el tema de las excepciones...
    # - agregar casos para metodos abstractos e interfaces

    def setUp(self):
        self.parser = CSharpMethodParser();
        self.class_model = Class('global', 'Foo', '', False, '', 'C#')
    
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
        
    def test_get_documentation(self):
        ''' Test getting the documentation. '''
        content = [
            "public void foo() { doSomething(); }",
            
            "// This is the doc...",
            "public void foo(int bar) { doSomething(); }",
            
            "public void foo() { doSomething() } //this is another doc...",
            
            "/// <summary>",
            "/// This is the sort doc...",
            "/// </summary>",
            "/// This is found in the long doc...",
            "public void foo() { doSomething() }",
        "}"
        ]
        index, method = self.parser.parse(self.class_model, content, 0)
        self.assertEquals(index, 1)
        self.assertEquals(method.short_documentation, None)
        self.assertEquals(method.long_documentation, None)        
        
        index, method = self.parser.parse(self.class_model, content, 2)
        self.assertEquals(index, 3)
        self.assertEquals(method.short_documentation, "This is the doc...")
        self.assertEquals(method.long_documentation, "This is the doc...") 
        
        index, method = self.parser.parse(self.class_model, content, 3)
        self.assertEquals(index, 4)
        self.assertEquals(method.short_documentation, None)
        self.assertEquals(method.long_documentation, None)        
        
        index, method = self.parser.parse(self.class_model, content, 8)
        self.assertEquals(index, 9)
        self.assertEquals(method.short_documentation, "This is the sort doc...")
        self.assertEquals(method.long_documentation, "<summary>This is the sort doc...</summary>This is found in the long doc...")
        
        
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
            
            "public void foo(int bar5) {",
                "// this should be ingnored {",
                "doSomething();",
            "}",
            
            
            "public void foo(int bar6) {",
                "/**",
                "* this is commented code:",
                "* if (condition) { * /",
                "doSomething()",
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
        self.assertEquals(method.signature, 'void foo(int bar5)')
        
        index, method = self.parser.parse(self.class_model, content, 20)
        self.assertEquals(index, 26)
        self.assertEquals(method.signature, 'void foo(int bar6)')
        
        index, method = self.parser.parse(self.class_model, content, 26)
        self.assertEquals(index, 30)
        self.assertTrue(method is None)
                
        