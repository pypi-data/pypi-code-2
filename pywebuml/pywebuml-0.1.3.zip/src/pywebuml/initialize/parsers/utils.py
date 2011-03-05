# -*- coding: utf-8 -*-

"""
Has the different parsers used to get the data from a programming file.
"""


from pywebuml.initialize.parsers.csharp.file_parser import CSharpFileParser
from pywebuml.initialize.parsers.java import JavaParser
from pywebuml.initialize.parsers.python import PythonParser

def get_parser(file_extension):
    if file_extension == 'cs':
        return CSharpFileParser()
    elif file_extension == 'java':
        return JavaParser()
    else:
        return PythonParser()
