# -*- codign: utf-8 -*-

'''
Has different constants used in the different parsers.

@author: tzulberti
'''

# Methods or attributes modifiers. See:
# http://msdn.microsoft.com/en-us/library/6tcf2h8w%28v=vs.71%29.aspx
# TODO order them by name
MODIFIERS = [
    "abstract",
    "const",
    "event",
    "extern",
    "delegate",
    "new",
    "internal",
    "override",
    "private",
    "protected",
    "public",
    "readonly",
    "sealed",
    "static",
    "unsafe",
    "virtual",
    "volatile",
]


ABSTRACT_KEYWORDS = [
    "abstract",
    "delegate",
    "extern",
]

CLASS_KEYWORDS = [
    "class",
    "struct",
    "interface",
    "partial",
]

CONST_KEYWORDS = [
    "const",
    "readonly",
]

COMPILER_DIRECTIVES = [
    '#if',
    '#else',
    '#elif',
    '#endif',
    '#undef',
    '#define',
    '#warning',
    '#error',
    '#line',
    '#region',
    '#endregion',
    '#pragma',
    '#pragma warning',
    '#pragma checksum',
]

COMMENTS_MARKERS = [
    '//',
    '///',
    '/*',
    '/**',    
    '*/',    
    '*',
]

LANGUAGE_BASE_VALUES = [
    'int', 
    'float', 
    'double', 
    'long', 
    'string', 
    'char', 
    'boolean',
    'bool',
    'object',
    'Object',
    'enum',
    'String',
    'Boolean',
    'Integer',
    'Long',
    'Double',
    'BigInt',
]