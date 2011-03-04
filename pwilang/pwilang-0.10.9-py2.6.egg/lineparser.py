import ply.lex as lex
from common import *

tokens = (
    'ESCAPED',
    'TAG_START',
    # 'PYTHON_SIMPLE',
    # 'PYTHON_COMPLEX',
    'RBRAK',
    'LBRAK',
    'WORD',
    'DQUOTE',
    'SQUOTE',
    'DOT',
    'SHARP',
    'SPACE',
    'DATTR',
    'SATTR',
    'ANYTHING',
)

precedence = (
    ('right', 'TAG_START' ),
    ('right', 'DATTR', 'SATTR'),
    ('left', 'RBRAK', 'LBRAK'),
    ('left', 'DQUOTE', 'SQUOTE'),
    # ('left', 'PYTHON_SIMPLE', 'PYTHON_COMPLEX'),
    ('right', 'ANYTHING', 'WORD', 'SPACE' ), # The lowest
    ('left', 'DOT', 'SHARP'),
    ('left', 'ESCAPED' ),
)

escapes = {
    '<' : '&lt;',
    '>': '&gt;',
}

def t_ESCAPED (t):
    r'\\.'
    if escapes.has_key (t.value[1]):
        t.value = escapes[t.value[1]]
    else:
        t.value = t.value[1:]
    return t

def t_TAG_START (t):
    r'@/?\w[\w0-9_:-]*\s*'
    return t

"""
def t_PYTHON_SIMPLE (t):
    r'\$[\w_][\w0-9_.]*(\((\\.|[^\)])*\))?'
    t.value = t.value[1:].replace ('\\)', ')')
    # FIXME : unescape !
    return t

def t_PYTHON_COMPLEX (t):
    r'\$\s*\{(\\\}|[^\}])*\}'
    start = t.value.find ('{')
    t.value = t.value[start+1:-1].replace ('\\}', '}')
    return t
"""

def t_RBRAK (t):
    r'\]'
    return t
def t_LBRAK (t):
    r'\s*\['
    return t

def t_DQUOTE (t):
    r'"\s*'
    return t

def t_SQUOTE (t):
    r'\'\s*'
    return t

def t_DATTR (t):
    r'\s*\w[\w0-9_\-:]*="'
    return t

def t_SATTR (t):
    r'\s*\w[\w0-9_\-:]*=\''
    return t

def t_WORD (t):
    r'\s*\w[\w0-9_\-:]*\s*'
    return t

def t_DOT (t):
    r'\s*\.\w[\w0-9_:-]*\s*'
    return t

def t_SHARP (t):
    r'\s*\#\w[\w0-9_:-]*\s*'
    return t

def t_ANYTHING (t):
    r'[^\]]'
    return t

def t_error (t):
    print 'ERROR %s' % t.value

lexer = lex.lex ()

##################################### PARSER ####################################


##################################### PWiLang ####################################

from node import *
from os import getcwd, path

current_pwiline = None

def set_current_pwiline (pwiline):
    global current_pwiline
    current_pwiline = pwiline

class Modifiers (object):
    ''' Used to pass parsed modifiers to tags '''
    def __init__ (self):
        self.classes = []
        self.attrs = {}
        self.id = None

    def merge (self, merged):
        if merged.id:
            self.id = merged.id
        self.classes += merged.classes
        self.attrs.update (merged.attrs)
        return self

    def apply (self, tagnode):
        tagnode.classes = self.classes
        tagnode.attrs = self.attrs
        tagnode.id = self.id

def nodify (f, s=None):
    '''
        This function is used to collapse two following ContentNode into
        one (for exemple : 'toto${blublu}tatata' would in the end give three content
        nodes if blublu gives text).
        This is done for cosmetics.
    '''
    res = f

    if isinstance (f, str) or isinstance (f, unicode):
        f = ContentNode (f)
        f.line = current_pwiline
        if not s:
            return f
    else:
        f = f.last # We're only affecting the last node.

    if isinstance (s, str) or isinstance (s, unicode):
        s = ContentNode (s)
        s.line = current_pwiline

    if isinstance (f, ContentNode) and isinstance (s, ContentNode):
        # Merge the two content nodes in one.
        # return ContentNode (f.content + s.content)
        f.content += s.content
        f.last.next = s.next
    else:
        f.last.next = s

    return res

##################################### PLY YACC ####################################
# from pudb import set_trace

import ply.yacc as yacc

def p_top_level (p):
    '''
        top_level : contents
    '''
    p[0] = p[1]

def p_safe_tokens (p):
    '''
        safe_token :  ESCAPED
                    | WORD
                    | SPACE
                    | ANYTHING
    '''
    p[0] = nodify (p[1])

def p_modifiers (p):
    '''
        modifiers : modifiers_rec
                 | modifiers modifiers_rec
    '''
    p[0] = p[1]
    if len (p) == 3:
        p[0].merge (p[2])

def p_modifiers_rec (p):
    '''
        modifiers_rec :  DOT
                       | SHARP
    '''
    p[0] = Modifiers ()
    p[1] = p[1].strip ()
    if p[1].startswith ('.'):
        p[0].classes.append (p[1][1:])
    if p[1].startswith ('#'):
        p[0].id = p[1][1:]

import re
re_escaped = re.compile (r'\\(.)')

def p_tag (p):
    '''
        tag : TAG_START safe_token contents
            | TAG_START tag contents
            | TAG_START tag
            | TAG_START inline_contents
            | TAG_START safe_token
            | TAG_START

        tag_inside : TAG_START safe_token inline_contents_inside
            | TAG_START tag_inside inline_contents_inside
            | TAG_START tag_inside
            | TAG_START inline_contents
            | TAG_START safe_token
            | TAG_START
    '''
    t = TagNode (p[1])
    child = None
    if len (p) == 4:
        child = nodify (p[2], p[3])
    if len (p) == 3:
        if p[2]:
            child = nodify (p[2])
    if len (p[1]) > 1 and p[1][1] == '/':
        t.next = child
    else:
        t.appendChild (child)
    p[0] = t

def p_tag_modif (p):
    '''
        tag : TAG_START modifiers safe_token contents
            | TAG_START modifiers tag contents
            | TAG_START modifiers tag
            | TAG_START modifiers inline_contents
            | TAG_START modifiers safe_token
            | TAG_START modifiers

        tag_inside : TAG_START modifiers safe_token inline_contents_inside
            | TAG_START modifiers tag_inside inline_contents_inside
            | TAG_START modifiers tag_inside
            | TAG_START modifiers inline_contents
            | TAG_START modifiers safe_token
            | TAG_START modifiers
    '''
    t = TagNode (p[1])
    child = None
    mods = p[2]
    if len (p) == 5:
        child = nodify (p[3], p[4])
    if len (p) == 4:
        if p[3]:
            child = nodify (p[3])
    if len (p[1]) > 1 and p[1][1] == '/':
        t.next = child
    else:
        t.appendChild (child)
    p[2].apply (t)
    p[0] = t

def p_inline_contents (p):
    '''
        inline_contents : LBRAK inline_contents_inside RBRAK
                        | LBRAK RBRAK
    '''
    p[0] = None
    if len (p) == 4:
        p[0] = p[2]

def p_modifiers_rec_attrs (p):
    '''
        modifiers_rec : DATTR contents_dattr DQUOTE
                      | SATTR contents_sattr SQUOTE
                      | SATTR SQUOTE
                      | DATTR DQUOTE
    '''
    s = p[1]
    mods = Modifiers ()

    # FIXME : Add the rules
    att = s[:-2]

    if len (p) == 4:
        contents = nodify (p[2])
        contents.prev = nodify (p[3].strip ())
        contents.last.next = nodify (p[3].strip ())
        mods.attrs[att] = contents.prev
    else:
        mods.attrs[att] = nodify ('%s%s' % (p[2], p[2]))
    
    p[0] = mods

def p_contents_recursive (p):
    '''
        contents_rec : safe_token
                      | tag
                      | LBRAK
                      | RBRAK
                      | DOT
                      | SHARP
                      | DATTR
                      | SATTR
                      | DQUOTE
                      | SQUOTE
        inline_contents_inside_rec : safe_token
                                   | tag_inside
                                   | LBRAK
                                   | DOT
                                   | SHARP
                                   | DATTR
                                   | SATTR
                                   | DQUOTE
                                   | SQUOTE
        contents_sattr_rec : safe_token
                          | LBRAK
                          | RBRAK
                          | DOT
                          | SHARP
                          | DATTR
                          | DQUOTE
                          | SATTR
                          | TAG_START
        contents_dattr_rec : safe_token
                          | LBRAK
                          | RBRAK
                          | DOT
                          | SHARP
                          | DATTR
                          | SQUOTE
                          | SATTR
                          | TAG_START
    '''
    p[0] = nodify (p[1])

"""
def p_python_simple (p):
    '''
        safe_token : PYTHON_SIMPLE
                     | PYTHON_COMPLEX
    '''
    p[0] = CommandNode (p[1], current_pwiline)
"""

def p_contents (p):
    '''
        contents : contents_rec
        contents_sattr : contents_sattr_rec
        contents_dattr : contents_dattr_rec
        inline_contents_inside : inline_contents_inside_rec
    '''
    p[0] = nodify (p[1])

def p_contents_2 (p):
    '''
        contents : contents contents_rec
        contents_sattr : contents_sattr contents_sattr_rec
        contents_dattr : contents_dattr contents_dattr_rec
        inline_contents_inside : inline_contents_inside inline_contents_inside_rec
    '''
    p[0] = nodify (p[1], p[2])

def p_error (p):
    import common

    common.error_flag = True
    import pprint
    pprint.pprint (current_pwiline)
    print 'Error ' + repr (p)

parser = yacc.yacc (debug=None, tabmodule="pwilang.parsetab")

