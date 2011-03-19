# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

import random
from   random         import choice, randint, shuffle
import re
import os

# literals - common
ALPHANUM     = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
XWIKINAME_CH = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.'
SPECIALCHAR  = ' ~`!@%&:;"_,^\'.?+\\()$-\t'
ETCHARS      = '*#=-|'
PIPECHAR     = '|'
HPIPECHAR    = '|='
ESCCHAR      = '~'
LINKCHARS    = '[]'
MACROCHARS   = '{}'
HTMLCHARS    = '<>'
NEWLINE      = '\n'

ETMARKUP     = [ "''", '//', '__', '^^', ',,', "'/", "'_", "/_'","'/_", '\\\\', '[[', ']]',
                 '{{', '}}' ]
ETMARKUP_RE  = [ r"''", r'//', r'__', r'\^\^', r',,', r"'/", "'_", "/_'", r"'/_", r'\\\\',
                 r'\[\[', r'\]\]', r'{{', r'}}' ]
ORDMARKUP    = [ '*', '**', '***', '****', '*****' ]
STYLESHORTS  = [ '{c}', '{C}', '{|5}', '{5|}', '{\\1,solid,gray}' ]
UNORDMARKUP  = [ '#', '##', '###', '####', '#####' ]
BQMARKUP     = [ '>', '>>', '>>>', '>>>>', '>>>>>' ]
TBMARKUP     = [ '||{', '||}', '||-', '||=', '|| ' ]
alltext      = ALPHANUM + SPECIALCHAR + ETCHARS + LINKCHARS + MACROCHARS + HTMLCHARS

styles_elements = [ 
    { 'style' : 'color : black; background-color : white;' },
    { 'font-weight' : 'bold' },
    { 'font' : 'arial' },
    { 'width' : '100%' },
    { 'height' : '200px' },
]

# literals - to generate http and www uri
URI_RESRVED  = r':;/@&=,\?\#\+\$'
URI_MARK     = r"_!~'\(\)\*\.\-"
URI_ESCAPE   = r'%'
URI          = ALPHANUM + URI_RESRVED + URI_MARK + URI_ESCAPE

# literals - to generate links in wiki
linktext     = ALPHANUM + SPECIALCHAR + ETCHARS + MACROCHARS + HTMLCHARS

# literals - to generate macros in wiki
macrotext    = ALPHANUM + SPECIALCHAR + ETCHARS + LINKCHARS + HTMLCHARS + NEWLINE

# literals - to generate macros in wiki
htmltext     = ALPHANUM + SPECIALCHAR + ETCHARS + LINKCHARS + MACROCHARS + HTMLCHARS + \
               NEWLINE

# literals - to generate wiki content
wikilist = [ c for c in ALPHANUM + SPECIALCHAR + ETCHARS + PIPECHAR + \
                        ESCCHAR + LINKCHARS + MACROCHARS + HTMLCHARS + NEWLINE ] + \
                        ETMARKUP + ORDMARKUP + UNORDMARKUP + BQMARKUP + TBMARKUP + \
                        [ 'www.', 'http://' ]

# generate - http/www uri
_gen_httpuri = lambda uri=URI, n=100 : 'http://' + \
                          ''.join([ choice(uri) for i in range(randint(1,n))])
_gen_wwwuri  = lambda uri=URI, n=100 : 'www.' + \
                          ''.join([ choice(uri) for i in range(randint(1,n))])

# generate - format wiki words with markups
_formatwords = lambda m, w : m + ' ' + w + ' ' + m + ' '

# generate - list of link words
gen_linkwords = lambda linktext=linktext, maxlen=50, count=200 : \
                        [ ''.join([ choice( linktext )
                                    for i in range(randint( 1, maxlen )) ])
                          for i in range( count ) ]
# generate - link markup text
_gen_link     = lambda linkwords : '[[' + choice( linkwords ) + ']]' + ' '
# generate - list of links
gen_links    = lambda linkwords, count : \
                        [ _gen_link( linkwords ) for i in range( count ) ]

# generate - list of macro words
gen_macrowords= lambda macrotext=macrotext, maxlen=50, count=200 : \
                        [ ''.join([ choice( macrotext )
                                    for i in range(randint( 1, maxlen )) ])
                          for i in range( count ) ]
# generate - macro markup text
_gen_macro    = lambda macrowords : '{{' + choice( macrowords ) + '}}' + ' '
# generate - list of macros
gen_macros    = lambda macrowords, count :\
                        [ _gen_macro( macrowords ) for i in range( count ) ]

# generate - list of html words
gen_htmlwords = lambda htmltext=htmltext, maxlen=50, count=200 : \
                        [ ''.join([ choice( htmltext )
                                    for i in range(randint( 1, maxlen )) ])
                          for i in range( count ) ]
# generate - html markup text
_gen_html     = lambda htmlwords : "'<" + choice( htmlwords ) + ">'" + ' '
# generate - list of htmls
gen_htmls     = lambda htmlwords, count : \
                        [ _gen_html( htmlwords ) for i in range( count ) ]

# generate - list of wikinames
_gen_xwikiname = lambda maxlen : ''.join([ choice(XWIKINAME_CH)
                                           for i in range(randint(0,maxlen)) ])
gen_xwikinames = lambda count  : [ _gen_xwikiname( 25 ) for i in range(count) ]

# generate - wiki word
def _gen_word( wordlist ) :
    """Pick a text word from the pre generated list `wordlist` and strip off
    the markup characters and newline.
    The generated word is appended with space"""
    txt = choice( wordlist )
    for m in ETMARKUP_RE + [ '\n' ]  :
        txt = re.sub( m, '', txt, 10 ) 
    return txt + ' '
# generate - list of basic wiki words
gen_wordlist  = lambda alltext=alltext, maxlen=20, count=200: \
                        [ ''.join([ choice( alltext )
                                    for i in range(randint( 0, maxlen )) ])
                          for i in range(count) ]
# generate - list of full wiki words.
gen_words     = lambda wordlist, count=200, huri_c=10, wuri_c=10 : \
                    [ _gen_word( wordlist ) for i in range( count ) ] + \
                    [ _gen_httpuri() for i in range( huri_c ) ] + \
                    [ _gen_wwwuri() for i in range( wuri_c ) ]

# generate - page seperator
gen_psep     = lambda n : ''.join([ '\n' for i in range(randint(0,n)) ])

# Generate style shortcut
gen_stylesh  = lambda : choice(STYLESHORTS)

# generate - list markup
gen_ordmark  = lambda : choice(ORDMARKUP) + choice(STYLESHORTS)
gen_unordmark= lambda : choice(UNORDMARKUP) + choice(STYLESHORTS)
gen_bqmark   = lambda : choice(BQMARKUP)
gen_defnmark = lambda : ':' + \
                        ''.join([ choice(alltext) for i in range(50) ]) + \
                        '::'

# generate - heading content.
gen_headtext = lambda wordlist : choice( wordlist ).replace( '=', '' )

# generete - wiki text
def gen_texts( words, links, macros, htmls, tc=1, pc=1, ec=1, lc=1, mc=1, hc=1,
               fc=0, nopipe=True ) :
    """master text generation function to generate wiki text
    tc  no of wiki words
    pc  no of words with pipe-char ('|') injected inside.
    ec  no of words with escape-char ('~') injected inside.
    lc  no of links
    mc  no of macros
    hc  no of htmls
    fc  no of formatted texts
    nopipe=True
    """
    # Generate contents
    wordlist  = [ choice(words) for i in range(tc) ]
    pwordlist = [ choice(words)+PIPECHAR+choice(words) for i in range(pc) ]
    ewordlist = [ choice(words)+ESCCHAR+choice(words) for i in range(ec) ]
    linklist  = [ choice(links)  for i in range(lc) ]
    macrolist = [ choice(macros) for i in range(mc) ]
    htmllist  = [ choice(htmls)  for i in range(hc) ]
    fwordlist = [ _formatwords(
                    choice(ETMARKUP),
                    ''.join([ choice(words + ['\n' ])
                              for j in range(randint(0,200)) ])
                  ) for i in range(fc) ]
    # Aggregate, shuffle and join contents
    #   Remove the pipe if present as the first character in the generated text
    #   Make ~ as ~~, if found at the end of the generated text
    texts = wordlist + pwordlist + ewordlist + linklist + macrolist + htmllist + \
            fwordlist + [ '\n' ] * 10 + [ gen_psep(i) for i in range(10) ]
    shuffle( texts )
    texts = ((nopipe and choice(ALPHANUM)) or '') + ''.join( texts )
    texts = texts + ((texts[-1] == ESCCHAR and ESCCHAR) or '')
    return texts

# generate - table cell seperator
_gen_cellstart = lambda : ' ' * randint(0,3) + choice([ PIPECHAR, HPIPECHAR ]) + ' ' * randint(0,3)
_gen_tbmarkup  = lambda : ' ' * randint(0,3) + choice(TBMARKUP) + ' ' * randint(0,3)
# generate - table cells
def _gen_cell( words, links, macros, htmls ):
    """Generate a table cell."""
    wordlist  = [ choice(words) for i in range(randint(0,5)) ]
    ewordlist = [ choice(words)+ESCCHAR+choice(words)
                  for i in range( randint( 0,2 )) ]
    linklist  = [ choice(links) for i in range(randint(0,2)) ]
    macrolist = [ choice(macros) for i in range(randint(0,2)) ]
    htmllist  = [ choice(htmls) for i in range(randint(0,2)) ]
    fwordlist = [ _formatwords(
                    choice(ETMARKUP),
                    ''.join([ choice(words) for j in range(randint(0,200)) ])
                  ) for i in range(randint(0,2)) ]
    # Aggregate, shuffle, join contents
    #   Make ~ as ~~ if found at the end.
    cellwords = [ w.replace(PIPECHAR, '')
                  for w in wordlist + ewordlist + fwordlist ] +\
                linklist + macrolist + htmllist
    shuffle( cellwords )
    cell      = ''.join( cellwords )
    if cell and cell[-1] == ESCCHAR :
        cell = cell + ESCCHAR
    return _gen_cellstart() + cell 
# generate - table row
gen_row = lambda words, links, macros, htmls : \
                ''.join([ _gen_cell( words, links, macros, htmls ) 
                          for i in range(randint(0,4)) ]) + \
                _gen_cellstart()

# generate - table row
def gen_btableline( words, links, macros, htmls ) :
    wordlist  = [ choice(words) for i in range(randint(0,5)) ]
    ewordlist = [ choice(words)+ESCCHAR+choice(words)
                  for i in range( randint( 0,2 )) ]
    linklist  = [ choice(links) for i in range(randint(0,2)) ]
    macrolist = [ choice(macros) for i in range(randint(0,2)) ]
    htmllist  = [ choice(htmls) for i in range(randint(0,2)) ]
    fwordlist = [ _formatwords(
                    choice(ETMARKUP),
                    ''.join([ choice(words) for j in range(randint(0,200)) ])
                  ) for i in range(randint(0,2)) ]
    # Aggregate, shuffle, join contents
    #   Make ~ as ~~ if found at the end.
    cellwords = wordlist + ewordlist + linklist + macrolist + htmllist + fwordlist 
    # Styles options
    styles = {}
    [ styles.update( styles_elements[i] ) 
      for i in range(randint(0,len(styles_elements))) ]
    shuffle( cellwords )
    cell   = ''.join( cellwords )
    if cell and cell[-1] == ESCCHAR :
        cell = cell + ESCCHAR
    tbline = _gen_tbmarkup() + choice([ str(styles), '' ]) + \
              choice([ '|', '' ]) + cell
    return tbline
    
# random - textformatting
random_textformat = \
    lambda words, links, macros, htmls, count : \
      ''.join([ choice( words + links + macros + htmls + ETMARKUP )
                for i in range( count ) ])

# random - listformatting
def random_listformat( words, links, macros, htmls, newline, count ) :
    """Randomly generate wiki lists."""
    lines = count /10
    listitems  = ''
    for i in range( lines ) :
        listitems += choice(ORDMARKUP + UNORDMARKUP)
        for j in range(randint( 0, count )) :
            listitems += choice( words + links + macros + htmls + ETMARKUP + \
                                 ORDMARKUP + UNORDMARKUP  + BQMARKUP + TBMARKUP )
            count     -= 1
        listitems += newline
        if count < 0 :
            break
    return listitems
# random - blockquote formatting
def random_bqformat( words, links, macros, htmls, newline, count ) :
    """Randomly generate wiki blockquotes."""
    lines = count /10
    bqitems  = ''
    for i in range( lines ) :
        bqitems += choice(BQMARKUP)
        for j in range(randint( 0, count )) :
            bqitems += choice( words + links + macros + htmls + ETMARKUP + \
                               BQMARKUP + TBMARKUP + ORDMARKUP + UNORDMARKUP )
            count     -= 1
        bqitems += newline
        if count < 0 :
            break
    return bqitems
# random - definition formatting
def random_defnformat( words, links, macros, htmls, newline, count ) :
    """Randomly generate wiki definitions."""
    lines = count /10
    defnitems  = ''
    for i in range( lines ) :
        defnitems += gen_defnmark()
        for j in range(randint( 0, count )) :
            defnitems += choice( words + links + macros + htmls + ETMARKUP + \
                                 BQMARKUP + TBMARKUP + ORDMARKUP + UNORDMARKUP )
            count     -= 1
        defnitems += newline
        if count < 0 :
            break
    return defnitems
# random - tableformatting
def random_tableformat( words, links, macros, htmls, newline, count ) :
    """Randomly generate wiki lists."""
    lines = count /10
    row   = ''
    for i in range( lines ) :
        row += choice([ PIPECHAR, HPIPECHAR ])
        for j in range(randint( 0, count )) :
            row   += choice( words + links + macros + htmls + ETMARKUP + \
                             [ PIPECHAR, HPIPECHAR ] )
            count -= 1
        row += newline
        if count < 0 :
            break
    return row
# random - wiki
random_wikitext = lambda words, links, macros, htmls, count : \
                    ''.join([ choice( words + links + macros + htmls + ETMARKUP + \
                                      [ NEWLINE, PIPECHAR ] + ORDMARKUP + \
                                      UNORDMARKUP + BQMARKUP + TBMARKUP  )
                              for i in range( count ) ])
random_wiki     = lambda count : \
                    ''.join([ choice( wikilist ) for i in range( count ) ])

# literal - unicode
UNICODE = u''

def log_mheader( log, testdir, testfile, seed ) :
    logthead = ">> Setting up tests for `%s` with seed %s" % \
               ( os.path.join( testdir, testfile ), seed )
    print '\n', logthead
    log.info( logthead )

def log_mfooter( log, testfile, testdir ) :
    logttail = ">> Tearing down tests for `%s` " % \
               os.path.join( testdir, testfile )
    print logttail
    log.info( logttail )

def genseed() :
    return randint(1, 100000)
