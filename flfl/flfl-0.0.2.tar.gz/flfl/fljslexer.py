from ply import lex
import re

tokens = (
    'ADD_LET',
    'BREAK',
    'CASE',
    'CONTINUE',
    'DECREMENT',
    'DEFAULT',
    'DEFINE_BUTTON',
    'DEFINE_MC',
    'DIV_LET',
    'DO',
    'ELSE',
    'EQUAL',
    'FALSE',
    'FOR',
    'FUNCTION',
    'GRATER_EQUAL',
    'IDENTIFIER',
    'IF',
    'INCREMENT',
    'LESS_EQUAL',
    'LOGICAL_AND',
    'LOGICAL_OR',
    'MOD_LET',
    'MUL_LET',
    'NOT_EQUAL',
    'NULL',
    'NUMERIC_LITERAL',
    'RETURN',
    'STRING_LITERAL',
    'SUB_LET',
    'SWITCH',
    'THIS',
    'TRUE',
    'VAR',
    'WHILE'
    )

reserved = {
    'break': 'BREAK',
    'case': 'CASE',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'defineButton': 'DEFINE_BUTTON',
    'defineMc': 'DEFINE_MC',
    'do': 'DO',
    'else': 'ELSE',
    'false': 'FALSE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'if': 'IF',
    'null': 'NULL',
    'return': 'RETURN',
    'switch': 'SWITCH',
    'this': 'THIS',
    'true': 'TRUE',
    'var': 'VAR',
    'while': 'WHILE'
   }

t_ADD_LET = r"\+="
t_DECREMENT = r"--"
t_DIV_LET = r"/="
t_EQUAL = r"=="
t_LESS_EQUAL = r"<="
t_GRATER_EQUAL = r">="
t_INCREMENT = r"\+\+"
t_LOGICAL_AND = r"&&"
t_LOGICAL_OR = r"\|\|"
t_MOD_LET = r"%="
t_MUL_LET = r"\*="
t_NOT_EQUAL = r"!="
t_SUB_LET = r"-="


def t_SINGLELINE_COMMENT(t):
    r"//.*"
    pass

def t_MULTILINE_COMMENT(t):
    r'/\*(.|\n)*\*/'
    pass

def t_STRING_LITERAL(t):
    "\"(?:[^\"\\\\]|\\\\.)*\""
    r = re.compile("\"((?:[^\"\\\\]|\\\\.)*)\"")
    m = r.match(t.value)
    if m and m.group(1):
        s = m.group(1)
        t.value = str(s)
    else:
        t.value =  ''
    return t

def t_STRING_LITERAL2(t):
    '\'(?:[^\'\\\\]|\\\\.)*\''
    t.type = 'STRING_LITERAL'
    r = re.compile("\'((?:[^\"\\\\]|\\\\.)*)\'")
    m = r.match(t.value)
    if m and m.group(1):
        s = m.group(1)
        t.value = str(s)
    else:
        t.value = ''
    return t

def t_IDENTIFIER(t):
    r"[a-zA-Z\$\_][a-zA-Z0-9\$\_]*"
    t.type = reserved.get(t.value,'IDENTIFIER')
    if t.type=='None':
        t.value = None
    elif t.type=='FALSE':
        t.value = False
    elif t.type=='TRUE':
        t.value = True
    return t

def t_NUMERIC_LITERAL(t):
    r"(?:\d*\.\d+|\d+)"
    try:
        if t.value.find('.') >= 0:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
    except ValueError:
         print "Number %s is too large!" % t.value
         t.value = 0
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

literals = "(){}[];+-/*%<>=!:?,"
t_ignore = " \t"
bin_ops = ['||', '&&', '<', '<=', '>', '>=', '==', '+', '-', '/', '*', '%']
un_ops = ['!', '++$', '--$', '$++', '$--']

lex.lex()

if __name__ == '__main__':
    test = """
//hoge
var a = 100;
var hoge = 1.0+3;
var c = \"agagagaga\";
'hogehoge';
function f(a){
/*hogehoge*/
    return a+1;
}
for(var i=0;i<10;++i){
    a += 1;
}
if(a>10){
    a = 2;
}
f(hoge);
f(for(var i=0));
"""
    lex.input(test)
    while 1:
        t = lex.token()
        if not t: break
        print t
