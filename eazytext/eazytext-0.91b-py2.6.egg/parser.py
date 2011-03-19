# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Parser grammer for EazyText text"""

# -*- coding: utf-8 -*-

# Gotcha : None
#   1. Do not enable optimize for yacc-er. It optimizes the rules and the
#      rule handler fails.
#
# Notes  :
#   1. Currently the parser does not check for html characters in the
#      document.
#   2. Endmarker is appender to the wiki text to facilitate the wiki parsing.
#
# Todo   : 
#   ( The following lists needs be triaged )
#   * Mako to be integrated with EazyText as an extension.
#   * Explore the possible addition of `indentation` feature, like,
#       :some text          < one level indentation >
#       ::some text         < two level indentation >
#      while the indentation offset is configurable in the wiki style.
#      NOTE : indentation is not a feature of html. But can/should be achieved
#             via CSS
#   * Support merging table cells like (refer wiki-dot).
#   * Printable pages.
#   * Should we add the concept of variables and namespace ?
#   * Check out http://meta.wikimedia.org/wiki/Help:Variable and add them as
#     macros
#   * For Toc() macro add numbering feature.
#   * Math Macro (and extensions).
#   * Include macro to include pages from another wiki page.
#   * Social bookmarking.
#   * Flash support.
#   * When an ENDMARKER is detected by any grammar other than `wikipage`, it
#     can be indicated to the user, via translated HTML.
#   * While documenting the wiki, also document the original wiki texts that
#     gets consumed by wiki parsing and html translation.

import logging
import re
import sys
from   types    import StringType
import copy
from   os.path  import splitext, dirname
from   hashlib  import sha1

import ply.yacc

from   eazytext              import escape_htmlchars, split_style, \
                                    wiki_properties, ENDMARKER
from   eazytext.lexer        import ETLexer
from   eazytext.ast          import *
from   eazytext.macro        import loadmacros
from   eazytext.extension    import loadextensions

log = logging.getLogger( __name__ )
rootdir = dirname( __file__ )

# Default Wiki page properties
class ETParser( object ):
    skin_tmpl = '<style type="text/css"> %s </style>'

    def __init__(   self,
                    skin='default.css',
                    style={},
                    outputdir='',
                    obfuscatemail=False,
                    nested=False,
                    macrodir=None,
                    extdir=None,
                    stripscript=True,
                    lex_optimize=False,
                    lextab='eazytext.lextab',
                    lex_debug=False,
                    yacc_optimize=False,
                    yacctab='eazytext.yacctab',
                    yacc_debug=False,
                    app=None,
                ):
        """
        Create a new ETParser.
        : skin ::
            Either a CSS file (in which case the file name must end with '.css'
            extension) to be included in the generated HTML page.
            Or, HTML snippet to be included in the generated HTML page.
            If specified None, then no styling will be included inside the
            HTML file.
            
        : outputdir ::
            To change the directory in which the parsetab.py file (and other
            output files) are written.
                        
        : obfuscatemail ::
            Obfuscate email ids written using link markup.
            [[ mailto:<emailid> | text ]]

        : nested ::
            Extensions like Nested, and Box will do another level of
            eazytext parsing for its content.  If that is the case, then
            `nested` is set to True. Default is set to `False` which means
            this is the root invocation to parse wiki document.

        : macrodir ::
            List of directories to look for macro plugins. Each module is
            considered as a macro plugin.

        : extdir ::
            List of directories to look for wiki extension plugins. Each module
            is considered as an extension plugin.

        : stripscript ::
            HTML markup allows raw html to be interspeced with wiki text.
            Malicious users can inject use this to CSRF attacks. By setting
            this key word argument to True, all script tags found within HTML
            markup will be pruned away.

        : lex_optimize ::
            PLY-Lexer option.
            Set to False when you're modifying the lexer. Otherwise, changes
            in the lexer won't be used, if some lextab.py file exists.
            When releasing with a stable lexer, set to True to save the
            re-generation of the lexer table on each run.
            
        : lextab ::
            PLY-Lexer option.
            Points to the lex table that's used for optimized mode. Only if
            you're modifying the lexer and want some tests to avoid
            re-generating the table, make this point to a local lex table file
            (that's been earlier generated with lex_optimize=True)
            
        : lex_debug ::
            PLY-Yacc option.

        : yacc_optimize ::
            PLY-Yacc option.
            Set to False when you're modifying the parser. Otherwise, changes
            in the parser won't be used, if some parsetab.py file exists.
            When releasing with a stable parser, set to True to save the
            re-generation of the parser table on each run.
            
        : yacctab ::
            PLY-Yacc option.
            Points to the yacc table that's used for optimized mode. Only if
            you're modifying the parser, make this point to a local yacc table
            file.
                        
        : yacc_debug ::
            Generate a parser.out file that explains how yacc built the parsing
            table from the grammar.

        : app ::
            Application object that provides the standard objects to be used
            by EazyText.
        """
        self.app = app
        self.etlex = ETLexer( error_func=self._lex_error_func )
        self.etlex.build(
            optimize=lex_optimize, lextab=lextab, debug=lex_debug
        )
        self.tokens = self.etlex.tokens
        self.parser = ply.yacc.yacc( module=self, 
                                     debug=yacc_debug,
                                     optimize=yacc_optimize,
                                     tabmodule=yacctab,
                                     outputdir=outputdir
                                     # debuglog=log
                                   )
        self.parser.etparser = self     # For AST nodes to access `this`
        self.style = list(split_style( style ))
        self.wikiprops = {}
        self.dynamictext = False
        self.debug = lex_debug or yacc_debug
        self.obfuscatemail = obfuscatemail
        self.nested = nested
        self.stripscript = stripscript
        self.skin = self._fetchskin( skin )

        macrodir = [ macrodir
                   ] if isinstance(macrodir,basestring) else macrodir
        extdir = [ extdir ] if isinstance(extdir,basestring) else extdir
        macrodir and map( loadmacros, macrodir )
        extdir and map( loadextensions, extdir )
    
    def _fetchskin( self, skin ) :
        if skin == None :
            self.skin = ''
        elif splitext( skin )[-1] == '.css' :
            csscont = open(join(rootdir, 'skins', skin)).read()
            self.skin = self.skin_tmpl % csscont
        else :
            self.skin = skin

    def _wiki_preprocess( self, text ) :
        """The text to be parsed is pre-parsed to remove and fix unwanted
        side effects in the parser.
        Return the preprossed text"""
        # Replace `~ ESCAPEd new lines`.
        text = re.compile( r'~+\n', re.MULTILINE | re.UNICODE ).sub('\n', text)
        text = text.rstrip( '~' )   # Remove trailing ESCAPE char
        # Replace `\ ESCAPEd new lines'.
        text = text.replace( '\\\n', '' )
        return text

    def parse( self, text, nested=None, skin=None,
               filename='', debuglevel=0 ):
        """Parses eazytext-markup //text// and creates an AST tree. For every
        parsing invocation, the same lex, yacc, app options and objects will
        be used.

        : nested ::
            A string containing the Wiki text
        : text ::
            A string containing the Wiki text
        : filename ::
            Name of the file being parsed (for meaningful error messages)
        : debuglevel ::
            Debug level to yacc
        """

        # Initialize
        self.etlex.filename = filename
        self.etlex.reset_lineno()
        self.text = text
        self.wikiprops = {}
        self.macroobjects = []  # Macro objects detected while parsing
        self.extobjects = []    # Extension objects detected while parsing
        self.prehtmls = []      # html goes before actual translated text
        self.posthtmls = []     # html goes after actual translated text
        self.styleattr = ''
        self.hashtext = sha1( text ).hexdigest()
        self.nested = self.nested if nested == None else nested
        self.skin = self.skin if skin == None else self._fetchskin( skin )

        # Parse wiki properties, returned `props` contains only styling
        # (key,value) pairs
        props, text = wiki_properties( text )
        d_style, s_style = split_style( props )
        style = copy.deepcopy( self.style )
        style[0].update( d_style )
        style[1] += ('; ' + s_style) if s_style else ''
        fn = lambda x  : '%s : %s' % (x[0], x[1])
        self.styleattr = '; '.join( map( fn, style[0].items() ))
        self.styleattr += ('; ' + style[1]) if self.style[1] else ''

        # Pre-process the text, massage them for prasing.
        self.pptext = self._wiki_preprocess( text )

        # parse and get the Translation Unit
        self.pptext += '\n' + ENDMARKER
        self.tu = self.parser.parse( self.pptext,
                                     lexer=self.etlex,
                                     debug=debuglevel )
        return self.tu

    # ---------------------- Interfacing with Macro Core ----------------------

    def regmacro( self, macroobject ) :
        """
        Register the Macro node with the parser, so that pre and post html
        processing can be done. This is automatically handled by the macro
        framework.
        """
        self.macroobjects.append( macroobject )

    def onprehtml_macro( self ) :
        """
        Before tohtml() method is called on the Node tree, all the
        registered macroobject's on_prehtml() method will be called, which
        should return a tuple of,
            (weight, html)
        higher the //weight//, earlier the //html// content will be positioned.
        This is automatically handled by the macro framework.
        """
        for m in self.macroobjects :
            rc = m.on_prehtml()
            self.prehtmls.append(rc) if rc else None
        
    def onposthtml_macro( self ) :
        """
        After tohtml() method is called on the Node tree, all the
        registered macroobject's on_posthtml() method will be called, which
        should return a tuple of,
            (weight, html)
        higher the //weight//, earlier the //html// content will be positioned.
        This is automatically handled by the macro framework.
        """
        for m in self.macroobjects :
            rc = m.on_posthtml()
            self.posthtmls.append(rc) if rc else None

    # ---------------------- Interfacing with Extension Core ------------------

    def regext( self, extobject ) :
        """
        Register the NoWiki node with the parser, so that pre and post html
        processing can be done. This is automatically handled by extension
        framework.
        """
        self.extobjects.append( extobject )
    
    def onprehtml_ext( self ) :
        """
        Before tohtml() method is called on the Node tree, all the
        registered extension-obj's on_prehtml() method will be called, which
        should return a tuple of,
            (weight, html)
        higher the //weight//, earlier the //html// content will be positioned.
        This is automatically handled by the macro framework.
        """
        for e in self.extobjects :
            rc = e.on_prehtml()
            self.prehtmls.append(rc) if rc else None
        
    def onposthtml_ext( self ) :
        """
        After tohtml() method is called on the Node tree, all the
        registered extension-obj's on_posthtml() method will be called, which
        should return a tuple of,
            (weight, html)
        higher the //weight//, earlier the //html// content will be positioned.
        This is automatically handled by the macro framework.
        """
        for e in self.extobjects :
            rc = e.on_posthtml()
            self.posthtmls.append(rc) if rc else None

    # ------------------------- Private functions -----------------------------

    def _lex_error_func( self, msg, line, column ):
        self._parse_error( msg, self._coord( line, column ))
    
    def _coord( self, lineno, column=None ):
        return Coord( file=self.etlex.filename, 
                      line=lineno,
                      column=column
               )
    
    def _parse_error(self, msg, coord):
        raise ParseError("%s: %s" % (coord, msg))

    def _printparse( self, p ) :
        print p[0], "  : ",
        for i in range(1,len(p)) :
            print p[i],
        print

    # ---------- Precedence and associativity of operators --------------------

    precedence = (
        ( 'left', 'PREC_LINK', 'PREC_MACRO', 'PREC_HTML' ),
    )
    
    def p_wikipage( self, p ):                          # WikiPage
        """wikipage             : paragraphs
                                | paragraphs ENDMARKER"""
        if len(p) == 2 :
            p[0] = Wikipage( p.parser, p[1] )
        elif len(p) == 3 :
            p[0] = Wikipage( p.parser, p[1] )
        else :
            raise ParseError( "unexpected rule-match for wikipage")

    def p_paragraphs( self, p ):                        # Paragraphs
        """paragraphs           : paragraph paragraph_separator
                                | paragraphs paragraph paragraph_separator
                                | paragraph_separator"""
        if len(p) == 2 :
            p[0] = Paragraphs( p.parser, p[1] )
        elif len(p) == 3 :
            p[0] = Paragraphs( p.parser, p[1], p[2] )
        elif len(p) == 4 :
            p[0] = Paragraphs( p.parser, p[1], p[2], p[3] )
        else :
            raise ParseError( "unexpected rule-match for paragraphs")

    def p_paragraph( self, p ):                         # Paragraph
        """paragraph            : nowikiblock
                                | heading
                                | horizontalrule
                                | btablerows
                                | table_rows
                                | orderedlists
                                | unorderedlists
                                | definitionlists
                                | blockquotes
                                | textlines"""
        p[0] = Paragraph( p.parser, p[1] )

    def p_nowiki( self, p ):                            # NoWiki
        """nowikiblock  : NOWIKI_OPEN NEWLINE nowikilines NOWIKI_CLOSE NEWLINE
                        | NOWIKI_OPEN NEWLINE nowikilines ENDMARKER"""
        if len(p) == 6 :
            p[0] = NoWiki( p.parser, p[1], p[2], p[3], p[4], p[5] )
        elif len(p) == 5 : 
            p[0] = NoWiki( p.parser, p[1], p[2], p[3], p[4], skip=True )

    def p_nowikilines( self, p ):
        """nowikilines          : empty
                                | NEWLINE
                                | nowikicontent NEWLINE
                                | nowikilines NEWLINE
                                | nowikilines nowikicontent NEWLINE"""
        if len(p) == 2 and isinstance( p[1], Empty ):
            p[0] = ''
        elif len(p) == 2 :
            p[0] = p[1]
        elif len(p) == 3 :
            p[0] = p[1] + p[2]
        elif len(p) == 4 :
            p[0] = p[1] + p[2] + p[3]
        else :
            raise ParseError( "unexpected rule-match for nowikilines")

    def p_nowikicontent( self, p ):
        """nowikicontent        : NOWIKI_CHARS
                                | NOWIKI_SPECIALCHAR
                                | NOWIKI_OPEN
                                | nowikicontent NOWIKI_OPEN
                                | nowikicontent NOWIKI_CHARS
                                | nowikicontent NOWIKI_SPECIALCHAR"""
        if len(p) == 2 :
            p[0] = p[1]
        elif len(p) == 3 :
            p[0] = p[1] + p[2]
        else :
            raise ParseError( "unexpected rule-match for nowikicontent")

    def p_heading( self, p ):                           # Heading
        """heading              : HEADING text_contents NEWLINE
                                | HEADING NEWLINE"""
        if len(p) == 4 :
            p[0] = Heading( p.parser, p[1], p[2], p[3] )
        elif len(p) == 3 :
            p[0] = Heading( p.parser, p[1], Empty( p.parser ), p[2] )
        else :
            raise ParseError( "unexpected rule-match for heading")

    def p_horizontalrule( self, p ):                    # HorizontalRule
        """horizontalrule       : HORIZONTALRULE NEWLINE"""
        p[0] = HorizontalRule( p.parser, p[1], p[2] )

    def p_textlines( self, p ) :                        # Textlines
        """textlines            : text_contents NEWLINE
                                | textlines text_contents NEWLINE"""
        if len(p) == 3 :
            p[0] = TextLines( p.parser, p[1], p[2] )
        elif len(p) == 4 and isinstance( p[1], TextLines ) :
            p[1].appendline( p[2], p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for textlines")

    def p_btablerows( self, p ):                        # BtableRows
        """btablerows       : btablerow
                            | btablerows btablerow"""
        if len(p) == 2 and isinstance( p[1], BtableRow ) :
            p[0] = BtableRows( p.parser, p[1] )
        elif len(p) == 3 and isinstance( p[1], BtableRows ) \
                         and isinstance( p[2], BtableRow ) :
            p[1].appendrow( p[2] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for btablerows")

    def p_btablerow( self, p ):                  # BtableRow+newline+text
        """btablerow        : btablerowbegin
                            | btablerow text_contents NEWLINE"""
        if len(p) == 2 :
            p[0] = p[1]
        elif len(p) == 4 :
            p[1].contlist( p.parser, p[2], p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for btablerow")

    def p_btablerowbegin_1( self, p ):                         # BtableRow
        """btablerowbegin   : BTABLE_START text_contents NEWLINE
                            | BTABLE_START empty NEWLINE"""
        p[0] = BtableRow( p.parser, p[1], p[2], p[3], type=FORMAT_BTABLE )

    def p_btablerowbegin_2( self, p ):                         # BtableRow
        """btablerowbegin   : BTABLESTYLE_START text_contents NEWLINE
                            | BTABLESTYLE_START empty NEWLINE"""
        p[0] = BtableRow( p.parser, p[1], p[2], p[3], type=FORMAT_BTABLESTYLE )

    def p_table_rows_1( self, p ):
        """table_rows       : table_cells NEWLINE
                            | table_cells TABLE_CELLSTART NEWLINE
                            | table_rows table_cells NEWLINE
                            | table_rows table_cells TABLE_CELLSTART NEWLINE"""
        if len(p) == 3 and isinstance( p[1], TableCells ):
            p[0] = TableRows( p.parser, p[1], newline=p[2] )

        elif len(p) == 4 and isinstance( p[1], TableCells ):
            p[0] = TableRows( p.parser, p[1], p[2], p[3] )

        elif len(p) == 4 and isinstance( p[1], TableRows ) \
                         and isinstance( p[2], TableCells ) :
            p[1].appendrow( p[2], newline=p[3] )
            p[0] = p[1]

        elif len(p) == 5 and isinstance( p[1], TableRows ) \
                         and isinstance( p[2], TableCells ) :
            p[1].appendrow( p[2], p[3], p[4] )
            p[0] = p[1]

        else :
            raise ParseError( "unexpected rule-match for table_rows_1")

    def p_table_rows_2( self, p):
        """table_rows       : TABLE_CELLSTART NEWLINE
                            | table_rows TABLE_CELLSTART NEWLINE"""
        if len(p) == 3 :
            p[0] = TableRows( p.parser,
                              TableCells( p.parser, p[1], Empty( p.parser ) ),
                              newline=p[2]
                            )
        elif len(p) == 4 :
            p[1].appendrow( TableCells( p.parser, p[2], Empty( p.parser ) ),
                            newline=p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for table_rows_2")

    def p_table_cells( self, p ):                       # TableCells
        """table_cells      : TABLE_CELLSTART text_contents
                            | TABLE_CELLSTART empty
                            | table_cells TABLE_CELLSTART empty
                            | table_cells TABLE_CELLSTART text_contents"""
        if len(p) == 3 and isinstance( p[2], Empty ) :
            p[0] = TableCells( p.parser, p[1], p[2] )
        elif len(p) == 3 :
            p[0] = TableCells( p.parser, p[1], p[2] )
        elif len(p) == 4 and isinstance( p[3], Empty ) :
            p[1].appendcell( p[2], p[3] )
            p[0] = p[1]
        elif len(p) == 4 :
            p[1].appendcell( p[2], p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for table_cells")

    def p_orderedlists( self, p ):                      # Lists
        """orderedlists : orderedlist
                        | orderedlists unorderedlist
                        | orderedlists orderedlist"""
        if len(p) == 2 and isinstance( p[1], List ) :
            p[0] = Lists( p.parser, p[1] )
        elif len(p) == 3 and isinstance( p[1], Lists ) \
                         and isinstance( p[2], List ) :
            p[1].appendlist( p[2] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for orderedlists")

    def p_unorderedlists( self, p ):                    # Lists
        """unorderedlists       : unorderedlist
                                | unorderedlists orderedlist
                                | unorderedlists unorderedlist"""
        if len(p) == 2 and isinstance( p[1], List ) :
            p[0] = Lists( p.parser, p[1] )
        elif len(p) == 3 and isinstance( p[1], Lists ) \
                         and isinstance( p[2], List ):
            p[1].appendlist( p[2] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for unorderedlists")

    def p_orderedlist( self, p ):                       # List+newline+text
        """orderedlist : orderedlistbegin
                       | orderedlist text_contents NEWLINE"""
        if len(p) == 2 :
            p[0] = p[1]
        elif len(p) == 4 :
            p[1].contlist( p.parser, p[2], p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for orderedlist")

    def p_orderedlistbegin( self, p ):                  # List
        """orderedlistbegin : ORDLIST_START text_contents NEWLINE
                            | ORDLIST_START empty NEWLINE"""
        p[0] = List( p.parser, LIST_ORDERED, p[1], p[2], p[3] )

    def p_unorderedlist( self, p ):                     # List+newline+text
        """unorderedlist : unorderedlistbegin
                         | unorderedlist text_contents NEWLINE"""
        if len(p) == 2 :
            p[0] = p[1]
        elif len(p) == 4 :
            p[1].contlist( p.parser, p[2], p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for unorderedlist")

    def p_unorderedlistbegin( self, p ):                # List
        """unorderedlistbegin   : UNORDLIST_START text_contents NEWLINE
                                | UNORDLIST_START empty NEWLINE"""
        p[0] = List( p.parser, LIST_UNORDERED, p[1], p[2], p[3] )

    def p_definitionlists( self, p ):                    # Definitions
        """definitionlists      : definitionlist
                                | definitionlists definitionlist"""
        if len(p) == 2 and isinstance( p[1], Definition ) :
            p[0] = Definitions( p.parser, p[1] )
        elif len(p) == 3 and isinstance( p[1], Definitions ) \
                         and isinstance( p[2], Definition ):
            p[1].appendlist( p[2] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for definitionlists")

    def p_definitionlist( self, p ):                    # Def..+Text+Newline
        """definitionlist       : definitionlistbegin
                                | definitionlist  text_contents NEWLINE"""
        if len(p) == 2 :
            p[0] = p[1]
        elif len(p) == 4 :
            p[1].contlist( p.parser, p[2], p[3] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for definitionlist")

    def p_definitionlistbegin( self, p ):               # Definition
        """definitionlistbegin  : DEFINITION_START text_contents NEWLINE
                                | DEFINITION_START empty NEWLINE"""
        p[0] = Definition( p.parser, p[1], p[2], p[3] )

    def p_blockquotes( self, p ):                       # BQuotes
        """blockquotes          : blockquote
                                | blockquotes blockquote"""
        if len(p) == 2 and isinstance( p[1], BQuote ) :
            p[0] = BQuotes( p.parser, p[1] )
        elif len(p) == 3 and isinstance( p[1], BQuotes ) \
                         and isinstance( p[2], BQuote ):
            p[1].appendlist( p[2] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for blockquotes")

    def p_blockquote( self, p ):                        # BQuote
        """blockquote           : BQUOTE_START text_contents NEWLINE
                                | BQUOTE_START empty NEWLINE"""
        p[0] = BQuote( p.parser, p[1], p[2], p[3] )

    def p_text_contents( self, p ) :                    # TextContents
        """text_contents        : basictext
                                | link
                                | macro
                                | html
                                | text_contents basictext
                                | text_contents link
                                | text_contents macro
                                | text_contents html"""
        if len(p) == 2 and isinstance( p[1], (Link,Macro,Html,BasicText) ):
            p[0] = TextContents( p.parser, p[1] ) 
        elif len(p) == 3 and isinstance( p[1], TextContents ) \
                         and isinstance( p[2], (Link,Macro,Html,BasicText) ) :
            p[1].appendcontent( p[2] )
            p[0] = p[1]
        else :
            raise ParseError( "unexpected rule-match for text_contents")

    def p_link( self, p ):                              # Link
        """link                 : LINK %prec PREC_LINK"""
        p[0] = Link( p.parser, p[1] )

    def p_macro( self, p ):                             # Macro
        """macro                : MACRO %prec PREC_MACRO"""
        p[0] = Macro( p.parser, p[1] )

    def p_html( self, p ):                             # Html
        """html                 : HTML %prec PREC_HTML"""
        p[0] = Html( p.parser, p[1] )

    def p_basictext_1( self, p ):
        """basictext            : PIPE"""
        p[0] = BasicText( p.parser, TEXT_CHARPIPE, p[1] )

    def p_basictext_2( self, p ):
        """basictext            : ALPHANUM"""
        p[0] = BasicText( p.parser, TEXT_ALPHANUM, p[1] )

    def p_basictext_3( self, p ):
        """basictext            : SPECIALCHAR
                                | TEXTMARKUPCHAR
                                | SQR_OPEN
                                | SQR_CLOSE
                                | PARAN_OPEN
                                | PARAN_CLOSE
                                | ANGLE_OPEN
                                | ANGLE_CLOSE"""
        p[0] = BasicText( p.parser, TEXT_SPECIALCHAR, p[1] )

    def p_basictext_4( self, p ):
        """basictext            : HTTP_URI
                                | HTTPS_URI"""
        p[0] = BasicText( p.parser, TEXT_HTTPURI, p[1] )

    def p_basictext_5( self, p ):
        """basictext            : WWW_URI"""
        p[0] = BasicText( p.parser, TEXT_WWWURI, p[1] )

    def p_basictext_6( self, p ):
        """basictext            : M_SPAN"""
        p[0] = BasicText( p.parser, TEXT_M_SPAN, p[1] )

    def p_basictext_7( self, p ):
        """basictext            : M_BOLD"""
        p[0] = BasicText( p.parser, TEXT_M_BOLD, p[1] )

    def p_basictext_8( self, p ):
        """basictext            : M_ITALIC"""
        p[0] = BasicText( p.parser, TEXT_M_ITALIC, p[1] )

    def p_basictext_9( self, p ):
        """basictext            : M_UNDERLINE"""
        p[0] = BasicText( p.parser, TEXT_M_UNDERLINE, p[1] )

    def p_basictext_10( self, p ):
        """basictext            : M_SUPERSCRIPT"""
        p[0] = BasicText( p.parser, TEXT_M_SUPERSCRIPT, p[1] )

    def p_basictext_11( self, p ):
        """basictext            : M_SUBSCRIPT"""
        p[0] = BasicText( p.parser, TEXT_M_SUBSCRIPT, p[1] )

    def p_basictext_12( self, p ):
        """basictext            : M_BOLDITALIC"""
        p[0] = BasicText( p.parser, TEXT_M_BOLDITALIC, p[1] )

    def p_basictext_13( self, p ):
        """basictext            : M_BOLDUNDERLINE"""
        p[0] = BasicText( p.parser, TEXT_M_BOLDUNDERLINE, p[1] )

    def p_basictext_14( self, p ):
        """basictext            : M_ITALICUNDERLINE"""
        p[0] = BasicText( p.parser, TEXT_M_ITALICUNDERLINE, p[1] )

    def p_basictext_15( self, p ):
        """basictext            : M_BOLDITALICUNDERLINE"""
        p[0] = BasicText( p.parser, TEXT_M_BOLDITALICUNDERLINE, p[1] )

    def p_basictext_16( self, p ):
        """basictext            : ESCAPED"""
        p[0] = BasicText( p.parser, TEXT_ESCAPED, p[1] )

    def p_paragraph_seperator( self, p ) :  # ParagraphSeparator
        """paragraph_separator  : NEWLINE
                                | paragraph_separator NEWLINE
                                | empty"""
        if len(p) == 2 :
            p[0] = ParagraphSeparator( p.parser, p[1] ) 
        elif len(p) == 3 :
            p[0] = ParagraphSeparator( p.parser, p[1], p[2] ) 
        else :
            raise ParseError( "unexpected rule-match for paragraph_separator" )

    def p_empty( self, p ):
        'empty : '
        p[0] = Empty( p.parser )
        
    def p_error( self, p ):
        if p:
            column = self.etlex._find_tok_column( p )
            self._parse_error( 'before: %s ' % p.value,
                               self._coord(p.lineno, column) )
        else:
            self._parse_error( 'At end of input', '' )

class Coord( object ):
    """ Coordinates of a syntactic element. Consists of:
        - File name
        - Line number
        - (optional) column number, for the Lexer
    """
    def __init__( self, file, line, column=None ):
        self.file   = file
        self.line   = line
        self.column = column

    def __str__( self ):
        str = "%s:%s" % (self.file, self.line)
        if self.column :
            str += ":%s" % self.column
        return str


class ParseError( Exception ):
    pass



if __name__ == "__main__":
    import pprint
    import time
    
    t1     = time.time()
    parser = ETParser(
                lex_optimize=True, yacc_debug=True, yacc_optimize=False
             )
    print time.time() - t1
    
    buf = ''' 
        int (*k)(int);
    '''
    
    # set debuglevel to 2 for debugging
    t = parser.parse( buf, 'x.c', debuglevel=0 )
    t.show( showcoord=True )
