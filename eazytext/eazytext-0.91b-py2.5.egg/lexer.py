#! /usr/bin/env python

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.


"""Lexing rules for EazyText text"""

# -*- coding: utf-8 -*-

# Gotcha :
#   1. Enabling optimize screws up the order of regex match (while lexing)
#      Bug in PLY ???
# Notes  :
#   1. The SPACE character is not getting detected for token BTABLE_START.
# Todo   :
#   1. Due to ordering issues the following functions are created from
#      simple regex variables.


import re
import sys
import logging

import ply.lex
from   ply.lex    import TOKEN

log = logging.getLogger( __name__ )

class ETLexer( object ) :
    """A lexer for the EazyText markup.
        build() To build   
        input() Set the input text
        token() To get new tokens.
    The public attribute filename can be set to an initial filaneme, but the
    lexer will update it upon #line directives."""

    ## -------------- Internal auxiliary methods ---------------------

    def _error( self, msg, token ):
        location = self._make_tok_location( token )
        self.error_func and self.error_func(self, msg, location[0])
        self.lexer.skip( 1 )
        log.error( "%s %s" % (msg, token) )
    
    def _find_tok_column( self, token ):
        i = token.lexpos
        while i > 0:
            if self.lexer.lexdata[i] == '\n': break
            i -= 1
        return (token.lexpos - i) + 1
    
    def _make_tok_location( self, token ):
        return ( token.lineno, self._find_tok_column(token) )
    
    ## --------------- Interface methods ------------------------------

    def __init__( self, error_func=None, conf={} ):
        """ Create a new Lexer.
        error_func :
            An error function. Will be called with an error message, line
            and column as arguments, in case of an error during lexing.
        """
        self.error_func = error_func
        self.filename = ''
        self.conf = conf

    def build( self, **kwargs ) :
        """ Builds the lexer from the specification. Must be called after the
        lexer object is created. 
            
        This method exists separately, because the PLY manual warns against
        calling lex.lex inside __init__"""
        self.lexer = ply.lex.lex( module=self,
                                  reflags=re.MULTILINE | re.UNICODE,
                                  **kwargs
                                )

    def reset_lineno( self ) :
        """ Resets the internal line number counter of the lexer."""
        self.lexer.lineno = 1

    def input( self, text ) :
        """`text` to tokenise"""
        self.lexer.input( text )
    
    def token( self ) :
        """Get the next token"""
        tok = self.lexer.token()
        return tok 

    # States
    states = (
               ( 'nowiki', 'exclusive' ),
               ( 'table',  'exclusive' ),
             )

    ## Tokens recognized by the ETLexer
    tokens = (
        # RegEx tokens.
        'PIPE', 'ALPHANUM',  'SPECIALCHAR', 'SQR_OPEN', 'SQR_CLOSE',
        'PARAN_OPEN', 'PARAN_CLOSE', 'ANGLE_OPEN', 'ANGLE_CLOSE', 'HTTP_URI',
        'HTTPS_URI', 'WWW_URI', 'TEXTMARKUPCHAR',

        # Line markups
        'HORIZONTALRULE', 'HEADING', 'BTABLE_START', 'BTABLESTYLE_START', 
        'ORDLIST_START', 'UNORDLIST_START',
        'DEFINITION_START', 'BQUOTE_START', 'TABLE_CELLSTART',

        # Block markups
        'NOWIKI_OPEN', 'NOWIKI_CLOSE', 'NOWIKI_CHARS', 'NOWIKI_SPECIALCHAR',

        # Text markups 
        'M_SPAN', 'M_BOLD', 'M_ITALIC', 'M_UNDERLINE', 'M_SUPERSCRIPT',
        'M_SUBSCRIPT', 'M_BOLDITALIC', 'M_BOLDUNDERLINE', 'M_ITALICUNDERLINE',
        'M_BOLDITALICUNDERLINE',

        # Special tokens
        'LINK', 'MACRO', 'HTML',
        'NEWLINE', 'ESCAPED',
        'ENDMARKER',
    )

    ## Rules for the lexer.

    def t_HORIZONTALRULE( self, t ):
        r'^-{4,}[ \t]*$'
        return t

    def t_HEADING( self, t ):
        r'^(([ \t]*={1,5})|([ \t]*[hH][12345]\.))(\{[^{}\r\n]*\})?'
        return t

    def t_BTABLESTYLE_START( self, t ) :
        r'^[ \t]*\|\|[=\-\{\} ][ \t]*\{[^\r\n]*\}[ \t]*\|'
        return t

    def t_BTABLE_START( self, t ) :
        r'^[ \t]*\|\|[ =\-{}]'
        return t

    def t_NOWIKI_OPEN( self, t ) :
        r'^{{{[ \t]*[a-zA-Z0-9_\-\. ]*[ \t]*$'
        t.lexer.push_state('nowiki')
        return t

    def t_nowiki_NOWIKI_OPEN( self, t ):
        r'^{{{[ \t]*[a-zA-Z0-9_\-\. ]*[ \t]*$'
        return t

    def t_nowiki_NOWIKI_CLOSE( self, t ):
        r'^[ \t]*}}}$'
        t.lexer.pop_state()
        return t

    def t_nowiki_ENDMARKER( self, t ):  
        r'\<\{\<\{\}\>\}\>'
        return t

    def t_nowiki_NOWIKI_CHARS( self, t ):  
        r'[^{}\r\n]+'
        return t

    def t_nowiki_NEWLINE( self, t ):
        r'(\r?\n)|\r'
        return t

    def t_nowiki_NOWIKI_SPECIALCHAR( self, t ):  
        r'[{}]'
        return t

    def t_TABLE_CELLSTART( self, t ):
        r'^[ \t]*\|=?(\{[^{}\r\n]*\})?'
        t.lexer.push_state('table')
        return t

    def t_table_TABLE_CELLSTART( self, t ):
        r'[ \t]*\|=?(\{[^{}\r\n]*\})?'
        return t

    def t_table_NEWLINE( self, t ):
        r'(\r?\n)|\r'
        t.lexer.pop_state()
        return t

    def t_table_ESCAPED( self, t ):
        r'~.'
        t.value = t.value[1]
        return t

    def t_table_LINK( self, t ):
        r'\[\[[^\[\]\r\n]+\]\]'
        return t

    def t_table_MACRO( self, t ):
        r'\{\{[^\r\n]+\}\}'
        return t

    def t_table_HTML( self, t ):
        r'\[<(.|[\n])+?>\]'
        return t

    def t_table_M_SPAN( self, t ) :
        r"``(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_BOLDITALICUNDERLINE( self, t ) :
        r"('/_|_/')(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_BOLD( self, t ) :
        r"''(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_ITALIC( self, t ) :
        r"//(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_UNDERLINE( self, t ) :
        r"__(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_SUPERSCRIPT( self, t ) :
        r"\^\^(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_SUBSCRIPT( self, t ) :
        r",,(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_BOLDITALIC( self, t ) :
        r"('/|/')(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_ITALICUNDERLINE( self, t ) :
        r"(/_|_/)(\{[^{}\r\n]*\})?"
        return t

    def t_table_M_BOLDUNDERLINE( self, t ) :
        r"('_|_')(\{[^{}\r\n]*\})?"
        return t

    def t_ORDLIST_START( self, t ):
        r'^[ \t]*\#{1,5}(\{[^{}\r\n]*\})?'
        return t

    def t_UNORDLIST_START( self, t ):
        r'^[ \t]*\*{1,5}(\{[^{}\r\n]*\})?'
        return t

    def t_DEFINITION_START( self, t ):
        r'^[ \t]*:[^\n\r]*::'
        return t

    def t_BQUOTE_START( self, t ):
        r'^[ \t]*\>{1,5}'
        return t

    def t_LINK( self, t ):
        r'\[\[[^\[\]\r\n]+\]\]'
        return t

    def t_MACRO( self, t ):
        r'\{\{([\n]|.)+?\}\}'
        return t

    def t_HTML( self, t ):
        r'\[<(.|[\n])+?>\]'
        return t

    def t_ESCAPED( self, t ):
        r'~.'
        t.value = t.value[1]
        return t

    def t_NEWLINE( self, t ):
        r'(\r?\n)|\r'
        return t

    def t_M_SPAN( self, t ) :
        r"``(\{[^{}\r\n]*\})?"
        return t

    def t_M_BOLDITALICUNDERLINE( self, t ) :
        r"('/_|_/')(\{[^{}\r\n]*\})?"
        return t

    def t_M_BOLD( self, t ) :
        r"''(\{[^{}\r\n]*\})?"
        return t

    def t_M_ITALIC( self, t ) :
        r"//(\{[^{}\r\n]*\})?"
        return t

    def t_M_UNDERLINE( self, t ) :
        r"__(\{[^{}\r\n]*\})?"
        return t

    def t_M_SUPERSCRIPT( self, t ) :
        r"\^\^(\{[^{}\r\n]*\})?"
        return t

    def t_M_SUBSCRIPT( self, t ) :
        r",,(\{[^{}\r\n]*\})?"
        return t

    def t_M_BOLDITALIC( self, t ) :
        r"('/|/')(\{[^{}\r\n]*\})?"
        return t

    def t_M_ITALICUNDERLINE( self, t ) :
        r"(/_|_/)(\{[^{}\r\n]*\})?"
        return t

    def t_M_BOLDUNDERLINE( self, t ) :
        r"('_|_')(\{[^{}\r\n]*\})?"
        return t

    def t_ENDMARKER( self, t ):  
        r'\<\{\<\{\}\>\}\>'
        return t

    # Tokenize Complex regex
    http_schema    = r'http://'
    https_schema   = r'https://'
    www_domain     = r'www\.'
    uri_reserved   = r':;/@&=,\?\#\+\$'
    uri_mark       = r"_!'\(\)\*\.\-"
    uri_escape     = r'%'
    http_uri       = http_schema + r'[a-zA-Z0-9' + uri_escape + uri_reserved + uri_mark + r']+'
    https_uri      = https_schema + r'[a-zA-Z0-9' + uri_escape + uri_reserved + uri_mark + r']+'
    www_uri        = www_domain + r'[a-zA-Z0-9' + uri_escape + uri_reserved + uri_mark + r']+'

    @TOKEN(http_uri)
    def t_HTTP_URI( self, t ):
        return t

    @TOKEN(https_uri)
    def t_HTTPS_URI( self, t ):
        return t

    @TOKEN(www_uri)
    def t_WWW_URI( self, t ):
        return t

    @TOKEN(http_uri)
    def t_table_HTTP_URI( self, t ):
        return t

    @TOKEN(https_uri)
    def t_table_HTTPS_URI( self, t ):
        return t

    @TOKEN(www_uri)
    def t_table_WWW_URI( self, t ):
        return t

    t_PIPE              = r'\|'
    t_ALPHANUM          = r'[a-zA-Z0-9]+'
    t_SQR_OPEN          = r'\['
    t_SQR_CLOSE         = r'\]'
    t_PARAN_OPEN        = r'\{'
    t_PARAN_CLOSE       = r'\}'
    t_ANGLE_OPEN        = r'\<'
    t_ANGLE_CLOSE       = r'\>'
    t_TEXTMARKUPCHAR    = r"['/_,`\^]"
    t_SPECIALCHAR       = r'[ !@%&:;=" \#\*\.\?\+\\\(\)\$\-\t]+'
    
    t_table_ALPHANUM    = r'[a-zA-Z0-9]+'
    t_table_SQR_OPEN    = r'\['
    t_table_SQR_CLOSE   = r'\]'
    t_table_PARAN_OPEN  = r'\{'
    t_table_PARAN_CLOSE = r'\}'
    t_table_ANGLE_OPEN  = r'\<'
    t_table_ANGLE_CLOSE = r'\>'
    t_table_TEXTMARKUPCHAR = r"['/_,`\^]"
    t_table_SPECIALCHAR = r'[ !@%&:;=" \#\*\.\?\+\\\(\)\$\-\t]+'

    def t_error( self, t ):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)

    def t_nowiki_error( self, t ):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)

    def t_table_error( self, t ):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)



if __name__ == "__main__":
    def errfoo(lex, msg, a, b):
        print msg, a, b
        sys.exit()
    
    text = "hello"
    etlex = ETLexer( errfoo )
    etlex.build()
    etlex.input( text )
    
    while 1:
        tok = etlex.token()
        if not tok: break
        print "-", tok.value, tok.type, tok.lineno, etlex.filename, tok.lexpos
