# * encoding: utf-8

__all__ = ['parse', 'SyntaxTree', 'FljsSyntaxError', 'SyntaxNode']

import ply.yacc as yacc
import ply.lex as lex
from os.path import join, dirname
from flfl.fljslexer import tokens, bin_ops

class FljsSyntaxError(Exception):
    def __init__(self, msg, line=None):
        self.message = msg
        self.lineno = line

class SyntaxTree:
    def __init__(self, o=None, t='LIST'):
        if o:
            self.children = o
        else:
            self.children = []
        self.type = t
        self.value = None
        self.lineno = None
        self.end_lineno = None
        self.children_with_key = {}
    def addWithKey(self, key, child):
        if not key in self.children_with_key:
            self.children_with_key[key] = SyntaxTree([child])
        else:
            self.children_with_key[key].append(child)
    def append(self, value):
        self.children.append(value)
    def __len__(self):
        return len(self.children)
    def __getitem__(self,key):
        if isinstance(key, int) or isinstance(key, slice):
            return self.children[key]
        elif key in self.children_with_key:
            return self.children_with_key[key]
        else:
            return SyntaxTree()
    def __setitem__(self,key,value):
        self.children[key] = value
    def __iter__(self):
        return self.children.__iter__()
    def __contains__(self, v):
        return v in self.children or v in self.children_with_key
    def to_s(self, level=1):
        if level >= 10:
            return '...'
        indent = "    " * level
        indent2 = "    " * (level-1)
        s = "{\n%stype: %s" % (indent, self.type)
        if self.value:
            s += ",\n"
            s += "%svalue: %s" % (indent, self.value)
        for k,v in self.children_with_key.iteritems():
            s += ","
            if isinstance(v, SyntaxTree):
                s += "\n%s%s: %s" % (indent, k, v.to_s(level+1))
            else:
                s += "\n%s%s: %s" % (indent, k, v)
        for k,v in enumerate(self.children):
            s += ","
            if isinstance(v, SyntaxTree):
                s += "\n%s%s: %s" % (indent, k, v.to_s(level+1))
            else:
                s += "\n%s%s: %s" % (indent, k, v)
        s += "\n%s}" % indent2
        return s
    def __repr__(self):
        return self.to_s()

class SyntaxNode():
    def __init__(self, v, t, lineno=None):
        self.type = t
        self.value = v
        self.lineno = lineno
    def __repr__(self):
       return "%s(%s)" % (self.type, self.value)
precedence = (
             ('left', 'LOGICAL_OR'),
             ('left', 'LOGICAL_AND'),
             ('nonassoc', '<', '>', 'GRATER_EQUAL', 'LESS_EQUAL', 'EQUAL'),
             ('left', '+','-'),
             ('left', '*', '/', '%'),
             ('right', 'INCREMENT', 'DECREMENT', '!'),
)

def p_program(p):
    '''program : global_source_elements'''
    p[0] = p[1]

def p_global_source_elements(p):
    '''global_source_elements : global_source_element
          | global_source_elements global_source_element'''

    if len(p)==3:
        p[0] = p[1]
        child = p[2]
    else:
        p[0] = SyntaxTree(None, 'PROGRAM')
        child = p[1]

    if child.type in ['DEFINE_FUNCTION', 'DEFINE_BUTTON', 'DEFINE_MC']:
        p[0].addWithKey(child.type, child)
    else:
        p[0].append(child)


def p_global_source_element(p):
    '''global_source_element : mc_source_element
          | button_declaration'''
    p[0] = p[1]

def p_mc_source_elements(p):
    '''mc_source_elements : empty
          | mc_source_element
          | mc_source_elements mc_source_element'''
    if p[1] is None:
        p[0] = SyntaxTree()
        return
    elif len(p)==2:
        p[0] = SyntaxTree(None, 'BLOCK')
        child = p[1]
    else:
        p[0] = p[1]
        child = p[2]

    if child.type =='DEFINE_FUNCTION':
        p[0].addWithKey(child.type, child)
    else:
        p[0].append(child)

def p_mc_source_element(p):
    '''mc_source_element : statement
          | function_declaration
          | mc_declaration'''
    p[0] = p[1]

def p_function_declaration(p):
    '''function_declaration : FUNCTION IDENTIFIER '(' formal_parameter_list__opt ')' '{' function_body '}' '''
    idf = SyntaxNode(p[2], 'IDENTIFIER', p.lineno(2))
    p[0] = SyntaxTree([idf, p[4], p[7]], 'DEFINE_FUNCTION')
    p[0].lineno = p.lineno(1)

def p_button_declation(p):
    '''button_declaration : DEFINE_BUTTON '(' NUMERIC_LITERAL ')' '{' handler_clauses '}' '''
    oid = SyntaxNode(p[3], 'NUMERIC')
    p[0] = SyntaxTree([oid, p[6]], 'DEFINE_BUTTON')
    p[0].lineno = p.lineno(1)

def p_mc_declaration(p):
    '''mc_declaration : DEFINE_MC '(' NUMERIC_LITERAL ')' '{' mc_source_elements '}' '''
    mid = SyntaxNode(p[3], 'NUMERIC')
    p[0] = SyntaxTree([mid, p[6]], 'DEFINE_MC')
    p[0].lineno = p.lineno(1)

def p_formal_parameter_list__opt(p):
    '''formal_parameter_list__opt : empty
          | formal_parameter_list'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = SyntaxTree(None)

def p_formal_parameter_list(p):
    '''formal_parameter_list : IDENTIFIER
           | formal_parameter_list ',' IDENTIFIER'''
    if len(p) == 3:
        idf = SyntaxNode(p[2], 'IDENTIFIER', p.lineno(2))
        p[1].append(idf)
        p[0] = p[1]
    else:
        idf = SyntaxNode(p[1], 'IDENTIFIER', p.lineno(1))
        p[0] = SyntaxTree([idf])

def p_function_body(p):
    '''function_body : empty
           | statement
           | function_body statement'''
    if len(p)==2 and not p[1]:
        p[0] = SyntaxTree(None, 'BLOCK')
    elif len(p)==2:
        p[0] = SyntaxTree([p[1]], 'BLOCK')
    elif len(p)==3:
        p[0] = p[1]
        p[0].append(p[2])

def p_handler_clauses(p):
    '''handler_clauses : handler_clause
          | handler_clauses handler_clause'''
    if len(p)==2:
        p[0] = SyntaxTree([p[1]], 'LIST')
    elif len(p)==3:
        p[0] = p[1]
        p[0].append(p[2])

def p_handler_clause(p):
    '''handler_clause : IDENTIFIER ':' '{' statement_list__opt '}'
          | call_expression ':' '{' statement_list__opt '}' '''
    if isinstance(p[1], str):
        v = SyntaxNode('IDENTIFIER', p[1], p.lineno(1))
    else:
        v = p[1]
    p[0] = SyntaxTree([v, p[4]], 'HANDLER')
    p[0].lineno = p.lineno(3)

def p_statement_list__opt(p):
    '''statement_list__opt : empty
          | statement_list'''
    if not p[1]:
        p[0] = SyntaxTree()
    else:
        p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement
          | statement_list statement'''
    if len(p)==2:
        p[0] = SyntaxTree([p[1]], 'BLOCK')
    elif len(p)==3:
        p[0] = p[1]
        p[0].append(p[2])

def p_statement(p):
    '''statement : block
          | variable_statement
          | empty_statement
          | expression_statement
          | if_statement
          | switch_statement
          | iteration_statement
          | return_statement
          | continue_statement
          | break_statement
          '''
    p[0] = p[1]

def p_block(p):
    '''block : '{' '}'
          | '{' statement_list '}' '''
    if len(p)==3:
        p[0] = SyntaxTree(None, 'BLOCK')
    elif len(p)==4:
        p[0] = SyntaxTree(p[2], 'BLOCK')

def p_variable_statement(p):
    '''variable_statement : VAR variable_declaration_list ';' '''
    if len(p[2])==1:
        p[0] = p[2]
    else: #複数のvarがある場合は単にblockとして扱う
        p[0] = SyntaxTree(p[2], 'BLOCK')
        p[0].lineno = p.lineno(2)

def p_variable_declaration_list(p):
    '''variable_declaration_list : variable_declaration
          | variable_declaration_list ',' variable_declaration'''
    if len(p)==2:
        p[0] = SyntaxTree([p[1]], 'BLOCK')
    elif len(p)==4:
        p[0] = p[1]
        p[0].append(p[3])

def p_variable_declaration(p):
    '''variable_declaration : IDENTIFIER initialiser
        | IDENTIFIER'''
    idf = SyntaxNode(p[1], 'IDENTIFIER', p.lineno(1))
    if len(p)==3:
        p[0] = SyntaxTree([idf, p[2]], 'VAR')
        p[0].lineno = p.lineno(1)
    elif len(p)==2:
        p[0] = SyntaxTree([idf], 'VAR')
        p[0].lineno = p.lineno(1)

def p_initializer(p):
    '''initialiser : '=' expression'''
    p[0] = p[2]

def p_expression(p):
    '''expression : increment_or_decrement expression
        | expression increment_or_decrement
        | expression '*' expression
        | expression '/' expression
        | expression '%' expression
        | expression '+' expression
        | expression '-' expression
        | expression LESS_EQUAL expression
        | expression GRATER_EQUAL expression
        | expression EQUAL expression
        | expression NOT_EQUAL expression
        | expression '<' expression
        | expression '>' expression
        | '!' expression
        | expression LOGICAL_AND expression
        | expression LOGICAL_OR expression
        | conditional_expression
        | assignment_expression
        | call_expression
        | left_hand_side_expression
        | THIS
        | literal
        | array_literal
        | '(' expression ')' '''

    #type: ! || $$ + - * / % < > <= => == ++$ --$ $++ $--
    #= *= += -= /= %=
    #COND
    #CALL, IDENTIFIER, ARRAY_REF, PROPERTY_REF, THIS
    #ARRAY, NULL, BOOLEAN, STRING, NUMERIC
    if len(p)==4:
        if p[2] in bin_ops:
            p[0] = SyntaxTree([p[1], p[3]], p[2])
            p[0].lineno = p.lineno(1)
        elif p[0] == '(':
            p[0] = p[2]
    elif len(p)==3:
        if p[1]=='!':
            p[0] = SyntaxTree([p[2]], '!')
        elif p[1]=='++':
            p[0] = SyntaxTree([p[2]], '++$')
        elif p[1]=='--':
            p[0] = SyntaxTree([p[2]], '--$')
        elif p[2]=='++':
            p[0] = SyntaxTree([p[1]], '$++')
        elif p[2]=='--':
            p[0] = SyntaxTree([p[1]], '$--')
        p[0].lineno = p.lineno(1)
    elif len(p)==2:
        p[0] = p[1]

def p_assignment_expression(p):
    '''assignment_expression : left_hand_side_expression assignment_operator expression'''
    p[0] = SyntaxTree([p[1], p[3]], p[2])
    p[0].lineno = p.lineno(1)

def p_conditional_expression(p):
    '''conditional_expression : expression '?' expression ':' expression'''
    p[0] = SyntaxTree([p[1], p[3], p[5]], 'COND')
    p[0].lineno = p.lineno(1)

def p_left_hand_side_expression(p):
    '''left_hand_side_expression : IDENTIFIER
        | left_hand_side_expression '[' expression ']'
        | left_hand_side_expression '.' IDENTIFIER'''
    if len(p)==2:
        idf = SyntaxNode(p[1], 'IDENTIFIER', p.lineno(1))
        p[0] = idf
    elif len(p)==5:
        p[0] = SyntaxTree([p[1], p[3]], 'ARRAY_REF')
        p[0].lineno = p.lineno(1)
    elif len(p)==4:
        p[0] = SyntaxTree([p[1], p[3]], 'PROPERTY_REF')
        p[0].lineno = p.lineno(1)

def p_increment_or_decrement(p):
    '''increment_or_decrement : INCREMENT
        | DECREMENT'''
    p[0] = p[1]

def p_call_expression(p):
    '''call_expression : IDENTIFIER arguments'''
    idf = SyntaxNode(p[1], 'IDENTIFIER', p.lineno(1))
    p[0] = SyntaxTree([idf, p[2]], 'CALL')
    p[0].lineno = p.lineno(1)

def p_arguments(p):
    '''arguments : '(' ')'
        | '(' argument_list ')' '''
    if len(p)==3:
        p[0] = SyntaxTree()
    elif len(p)==4:
        p[0] = p[2]

def p_argument_list(p):
    '''argument_list : expression
        | argument_list ',' expression'''
    if len(p)==2:
        p[0] = SyntaxTree([p[1]])
    elif len(p)==4:
        p[0] = p[1]
        p[0].append(p[3])

def p_literal(p):
    '''literal : null_literal
        | boolean_literal
        | NUMERIC_LITERAL
        | STRING_LITERAL'''
    if isinstance(p[1], int) or isinstance(p[1], float):
        p[0] = SyntaxNode(p[1], 'NUMERIC', p.lineno(1))
    elif isinstance(p[1], str):
        p[0] = SyntaxNode(p[1], 'STRING', p.lineno(1))
    elif isinstance(p[1], SyntaxTree):
        p[0] = p[1]

def p_null_literal(p):
    '''null_literal : NULL'''
    p[0] = SyntaxNode(None, 'NULL', p.lineno(1))

def p_boolean_literal(p):
    '''boolean_literal : TRUE
        | FALSE'''
    p[0] = SyntaxNode(p[1], 'BOOLEAN', p.lineno(1))

def p_empty_statement(p):
    '''empty_statement : ';' '''
    p[0] = SyntaxNode(None, 'EMPTY', p.lineno(1))

def p_expression_statement(p):
    '''expression_statement : expression ';' '''
    p[0] = SyntaxTree([p[1]], 'EXPRESSION_STATEMENT')
    p[0].lineno = p.lineno(1)

def p_if_statement(p):
    '''if_statement : IF '(' expression ')' statement ELSE statement
        | IF '(' expression ')' statement'''
    if len(p)==8:
        p[0] = SyntaxTree([p[3], p[5], p[7]], 'IF')
    elif len(p)==6:
        p[0] = SyntaxTree([p[3], p[5]], 'IF')
    p[0].lineno = p.lineno(5)

def p_iteration_statement(p):
    '''iteration_statement : DO statement WHILE '(' expression ')' ';'
        | WHILE '(' expression ')' statement
        | FOR '(' expression__opt ';' expression__opt ';' expression__opt ')' statement
        | FOR '(' VAR variable_declaration_list ';' expression__opt ';' expression__opt ')' statement'''
    if p[1]=='do':
        p[0] = SyntaxTree([p[2], p[5]], 'WHILE')
    elif p[1]=='while':
        p[0] = SyntaxTree([p[3], p[5]], 'WHILE')
    elif p[1]=='for':
        if len(p) == 10:
            p[0] = SyntaxTree([p[3], p[5], p[7], p[9]], 'FOR')
        elif len(p) == 11:
            p[0] = SyntaxTree([p[4], p[6], p[8], p[10]], 'FOR')
    p[0].lineno = p.lineno(1)

def p_expression__opt(p):
    '''expression__opt : empty
        | expression'''
    if not p[1]:
        p[0] = SyntaxTree()
    else:
        p[0] = p[1]

def p_continue_statement(p):
    '''continue_statement : CONTINUE ';' '''
    p[0] = SyntaxTree(None, 'CONTINUE')
    p[0].lineno = p.lineno(1)

def p_break_statement(p):
    '''break_statement : BREAK ';' '''
    p[0] = SyntaxTree(None, 'BREAK')
    p[0].lineno = p.lineno(1)

def p_return_statement(p):
    '''return_statement : RETURN
        | RETURN ';'
        | RETURN expression ';' '''
    if len(p)==2 or len(p)==3:
        p[0] = SyntaxTree(None, 'RETURN')
        p[0].lineno = p.lineno(1)
    elif len(p)==4:
        p[0] = SyntaxTree([p[2]], 'RETURN')
        p[0].lineno = p.lineno(1)

def p_switch_statement(p):
    '''switch_statement : SWITCH '(' expression ')' case_block'''
    p[0] = SyntaxTree([p[3], p[5]], 'SWITCH')
    p[0].lineno = p.lineno(1)

def p_case_block(p):
    '''case_block : '{' case_clauses__opt '}' '''
    p[0] = p[2]

def p_case_clauses__opt(p):
    '''case_clauses__opt : empty
        | case_clauses'''
    if not p[1]:
        p[0] = SyntaxTree(None)
    else:
        p[0] = p[1]

def p_case_clauses(p):
    '''case_clauses : case_clause
        | case_clauses case_clause'''
    if len(p)==2:
        p[0] = SyntaxTree([p[1]])
    elif len(p)==3:
        p[0] = p[1]
        p[0].append(p[2])

def p_case_clause(p):
    '''case_clause : CASE expression ':'
        | CASE expression ':' statement_list
        | default_clause'''
    if len(p)==4:
        p[0] = SyntaxTree([p[2]], 'CASE')
    elif len(p)==5:
        p[0] = SyntaxTree([p[2], p[4]], 'CASE')
    elif len(p)==2:
        p[0] = p[1]

def p_default_clause(p):
    '''default_clause : DEFAULT ':'
        | DEFAULT ':' statement_list'''
    if len(p)==3:
        p[0] = SyntaxTree([p[1]], 'CASE')
    elif len(p)==4:
        p[0] = SyntaxTree([p[1], p[3]], 'CASE')

def p_array_literal(p):
    '''array_literal : '[' elision ']'
        | '[' element_list ']'
        | '[' element_list ',' elision ']' '''
    if p[2]:
        p[0] = p[2]

def p_element_list(p):
    '''element_list : elision expression
        | element_list ',' elision expression'''
    if len(p)==3:
        p[0] =  SyntaxTree([p[2]], 'Array')
    elif len(p)==5:
        p[0] = p[1]
        p[0].append(p[4])

def p_elision(p):
    '''elision : empty
        | ','
        | elision ',' '''
    p[0] = None

def p_assignment_operator(p):
    '''assignment_operator : '='
        | MUL_LET
        | DIV_LET
        | MOD_LET
        | ADD_LET
        | SUB_LET'''
    p[0] = p[1]

def p_empty(p):
    '''empty : '''
    pass

def p_error(p):
    raise FljsSyntaxError("Syntax error: '%s'" % p.value, p.lineno)

def parse(s, confpath):
    parser = yacc.yacc(debug=0, outputdir=confpath)
    return parser.parse(s)


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
if(a>10){
    a = 2;
}
for(var i=0;i<10;++i){
    a += 1;
}
f(hoge);
"""
    r = parser.parse(test)
    print r
