# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# Note :
#   1. Project*() macros cannot be test via unit-testing. It can be tested
#      only in the context of zeta-app and a project under zeta-app

import logging
import unittest
import os
import difflib                as diff
import random
from   random                 import choice, randint, shuffle

from   nose.plugins.attrib    import attr
from   nose.tools             import assert_equal, assert_raises, assert_true, \
                                     assert_false
from   eazytext               import wiki_properties
from   eazytext.lexer         import ETLexer
from   eazytext.parser        import ETParser
import eazytext.test.testlib  as testlib
from   eazytext.test.testlib  import ETMARKUP, ETMARKUP_RE, \
                                     gen_psep, gen_ordmark, gen_unordmark, \
                                     gen_headtext, gen_texts, gen_row, \
                                     gen_wordlist, gen_words, gen_linkwords, \
                                     gen_links,gen_macrowords, gen_macros, \
                                     random_textformat, random_listformat, \
                                     random_tableformat, random_wikitext, \
                                     random_wiki, log_mheader,log_mfooter, genseed

log             = logging.getLogger(__name__)
seed            = None
stdfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'stdfiles' )
rndfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'rndfiles' )
samplefiles_dir = os.path.join( os.path.split( __file__ )[0], 'samplefiles' )
words           = None

image_macros   = [
( """{{ Image( 'http://assets0.twitter.com/images/twitter_logo_header.png', \
               'alternative text', href='http://www.google.com' ) }}""",
  [ '<img', 'src=', 'alt=', 'href=' ]
),
( """{{ Image( 'http://assets0.twitter.com/images/twitter_logo_header.png', \
               'alternative text', float='right' ) }}""",
  [ '<img', 'src=', 'alt=', 'style=', 'float', 'right' ]
),
( """{{ Image( 'http://assets0.twitter.com/images/twitter_logo_header.png', \
               'alternative text', href='http://www.google.com', \
               float='right' ) }}""",
  [ '<img', 'src=', 'alt=', 'href=', 'style=', 'float', 'right' ]
),
]

images_macro    = [
( 
 """{{ Images( \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/POD/m/matanuska-glacier-221184-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/Promotional/Geocore History/petra-pharaohs-treasure-377742-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Environment/Images/Habitat/drypowell-758749-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/POD/s/small-forest-elephants-684716-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/POD/b/bora-bora-aerial-view-513886-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/Content/churchill-aurora-407026-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/POD/h/holi-powder-518591-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/POD/b/boundless-biplane-509314-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/Content/purple-diatoms-527157-mn.jpg', \
 'http://photography.nationalgeographic.com/staticfiles/NGS/Shared/StaticFiles/Photography/Images/Content/shark-and-bubbles-689679-mn.jpg', \
 alt='alternate text', height='100px', width='100px', cols='3', \
 style="border : 3px solid gray;" ) }}
 """,
 [ 'matanuska', 'pharaohs', 'drypowell', 'elephants', 'bora', 'churchill',
   'powder', 'boundless', 'purple', 'bubbles', 'height=', 'width=', 'alt=',
   'style=' ]
)
]

def setUpModule( self ) :
    global words, seed

    testdir = os.path.basename( os.path.dirname( __file__ ))
    testfile= os.path.basename( __file__ )
    seed    = genseed()
    random.seed( seed )
    testlib.random.seed(  seed )
    log_mheader( log, testdir, testfile, seed )
    info    = "Initialising wiki ..."
    log.info( info )
    print info
    alphanum= 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    words   = [ ''.join([ choice( alphanum ) for i in range(randint(0, 20)) ])
                 for j in range( 1000 ) ]
    
def tearDownModule( self ) :
    testdir  = os.path.basename( os.path.dirname( __file__ ))
    testfile = os.path.basename( __file__ )
    log_mfooter( log, testdir, testfile )

class TestMacroDumpsRandom( object ) :
    """Test cases to validate Macro random"""

    def _test_execute( self, type, testcontent, count, ref='', cfunc=None  ) :
        # Initialising the parser
        etparser = ETParser( lex_optimize=True, yacc_optimize=False )

        # The first character is forced to be a `A` to avoid having `@` as the
        # first character
        testcontent = 'A' + testcontent

        # Characterize the generated testcontent set the wikiproperties
        wikiprops   = {}
        testcontent = ( "@ %s " % wikiprops ) + '\n' + testcontent
        
        # Test by comparing the dumps
        try :
            tu      = etparser.parse( testcontent, debuglevel=0 )
            result  = tu.dump()[:-1]
        except :
            tu     = etparser.parse( testcontent, debuglevel=2 )
            result = tu.dump()[:-1]

        # The reference is computed if no compare function (cfunc) is passed.
        if cfunc :
            cfunc( ref, tu )
        else :
            ref        = ref or testcontent
            ref        = etparser._wiki_preprocess( ref )
            props, ref = wiki_properties( ref )
            if result != ref :
                print ''.join(diff.ndiff( result.splitlines(1), ref.splitlines(1) ))
            assert result == ref, type+'... testcount %s'%count

    def test_0_file( self ) :
        """If file `ref` is available pick it and test it"""
        testlist  = []
        ref       = os.path.isfile( 'ref' ) and open( 'ref' ).read()
        ref and testlist.append( ref )
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'ref', t, testcount
            testcount += 1

    def test_1_clear( self ) :
        """Testing the Clear() macro"""
        print "\nTesting the Clear() macro"
        log.info( "Testing the Clear() macro" )
        testlist = [ '\n'.join([ gen_texts( words, [] , [], [],
                                            tc=5, pc=0, ec=0, lc=0, mc=0, hc=0, fc=0,
                                            nopipe=True
                                          )
                                 for j in range(randint(0,10)) ])
                     for k in range(100) ]
        clear_macros = [ '{{ Clear() }}', '{{Clear() }}', '{{ Clear() }}' ]

        def clear_cfunc( ref, tu ) :
            html= tu.tohtml()
            assert_true( 'class="etm-clear"' in html,
                         'Fail Clear Macro : %s ' % html )

        testcount = 1
        for t in testlist :
            off = randint( 0, len(t) )
            t   = t.replace( '{', '' )
            t   = t.replace( '}', '' )
            t   = t[:off] + choice( clear_macros ) + t[off:]
            yield self._test_execute, 'macro_clear', t, testcount, '', \
                  clear_cfunc
            testcount += 1

    def test_2_span( self ) :
        """Testing the Span() macro"""
        print "\nTesting the Span() macro"
        log.info( "Testing the Span() macro" )
        testlist = [ '\n'.join([ gen_texts( words, [], [], [],
                                            tc=5, pc=0, ec=0, lc=0, mc=0, hc=0, fc=0,
                                            nopipe=True
                                          )
                                 for j in range(randint(0,10)) ])
                     for k in range(100) ]
        span_macros = [ [ '{{ Span("Hello World") }}',
                          [ 'Hello World' ] ],
                        [ '{{ Span("How are you") }}',
                          [ 'How are you' ] ],
                        [ '{{ Span("With style", style={ "font-weight" : "bold"} ) }}',
                          [ 'With style', 'font-weight: bold' ] ] ,
                        [ '{{ Span("With kw styles", color="blue") }}',
                          [ 'With kw styles', 'color: blue' ] ]
                      ]

        def span_cfunc( macro_ref ) :
            def cfunc( ref, tu ) :
                html= tu.tohtml()
                [ assert_true( r in html and 'class="etm-span"' in html,
                               'Fail Span Macro : %s ' % html
                  ) for r in macro_ref ]
            return cfunc

        testcount = 1
        for t in testlist :
            off = randint( 0, len(t) )
            m   = choice( span_macros )
            t   = t[:off] + m[0] + t[off:]
            yield self._test_execute, 'macro_span', t, testcount, '', \
                  span_cfunc( m[1] )
            testcount += 1

    def test_3_redirect( self ) :
        """Testing the Redirect() macro"""
        print "\nTesting the Redirect() macro"
        log.info( "Testing the Redirect() macro" )
        testlist = [ '\n'.join([ gen_texts( words, [] , [], [],
                                            tc=5, pc=0, ec=0, lc=0, mc=0, hc=0, fc=0,
                                            nopipe=True
                                          )
                                 for j in range(randint(0,10)) ])
                     for k in range(100) ]
        redirect_macros = [ [ '{{ Redirect("Hello World") }}',
                              [ 'Hello World' ] ],
                            [ '{{ Redirect("/") }}',
                              [ '/' ] ],
                            [ '{{ Redirect("/hello/world") }}',
                              [ '/hello/world' ] ],
                          ]

        def redirect_cfunc( macro_ref ) :
            def cfunc( ref, tu ) :
                tu.tohtml()
                [ assert_true(
                    r == tu.parser.etparser.redirect, 'Fail Redirect Macro'
                  ) for r in macro_ref ]
            return cfunc

        testcount = 1
        for t in testlist :
            m   = choice( redirect_macros )
            t   = m[0] + t
            yield self._test_execute, 'macro_redirect', t, testcount, '', \
                  redirect_cfunc( m[1] )
            testcount += 1

    def test_4_html( self ) :
        """Testing the Html() macro"""
        print "\nTesting the Html() macro"
        log.info( "Testing the Html() macro" )
        testlist = [ '\n'.join([ gen_texts( words, [], [], [],
                                            tc=5, pc=0, ec=0, lc=0, mc=0, hc=0, fc=0,
                                            nopipe=True
                                          )
                                 for j in range(randint(0,10)) ])
                     for k in range(100) ]
        html_macros = [ [ '{{ Html("<table><tr><td>hello world</td></tr></table>") }}',
                          [ '<table><tr><td>hello world</td></tr></table>' ] ],
                      ]

        def html_cfunc( macro_ref ) :
            def cfunc( ref, tu ) :
                html= tu.tohtml()
                [ assert_true( r in html, 'Fail Html Macro : %s ' % html )
                  for r in macro_ref ]
            return cfunc

        testcount = 1
        for t in testlist :
            off = randint( 0, len(t) )
            m   = choice( html_macros )
            t   = t[:off] + m[0] + t[off:]
            yield self._test_execute, 'macro_html', t, testcount, '', \
                  html_cfunc( m[1] )
            testcount += 1

    def test_5_toc( self ) :
        """Testing the Toc() macro"""
        print "\nTesting the Toc() macro"
        log.info( "Testing the Toc() macro" )
        testlist = [ '\n'.join([ gen_texts( words, [], [], [],
                                            tc=5, pc=0, ec=0, lc=0, mc=0, hc=0, fc=0,
                                            nopipe=True
                                          )
                                 for j in range(randint(0,10)) ])
                     for k in range(100) ]
        toc_macros = [ '{{ Toc( indent=1 ) }}', '{{Toc() }}',
                       '{{ Toc( indent=2 ) }}' ]
        testcount = 1

        def toc_cfunc( ref, tu ) :
            html= tu.tohtml()
            assert_true( 'class="toc"' in html,
                         'Fail Toc Macro : %s ' % html )

        for t in testlist :
            t   = choice( toc_macros ) + t
            yield self._test_execute, 'macro_toc', t, testcount, '', \
                  toc_cfunc
            testcount += 1

    def test_6_image( self ) :
        """Testing the Image() macro"""
        print "\nTesting the Image() macro"""
        log.info( "Testing the Image() macro" )

        def img_cfunc( ref, tu ) :
            html= tu.tohtml()
            [ assert_true(
                    r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, r in image_macros :
            yield self._test_execute, 'macro_image', t, testcount, r, \
                  img_cfunc
            testcount += 1
            
    def test_7_images( self ) :
        """Testing the Images() macro"""
        print "\nTesting the Images() macro"
        log.info( "Testing the Images() macro" )
        
        def imgs_cfunc( ref, tu ) :
            html = tu.tohtml()
            [ assert_true( r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, r in images_macro :
            yield self._test_execute, 'macro_images', t, testcount, r, \
                  imgs_cfunc
            testcount += 1

    @attr(type='yb')
    def test_8_yearsbefore( self ) :
        """Testing the YearsBefore() macro"""
        print "\nTesting the YearsBefore() macro"
        log.info( "Testing the YearsBefore() macro" )
        
        ybtext = [
            ( """It happened {{ YearsBefore( '%s before', '2007', '9' ) }}""",
              [ 'span', 'year', 'month' ]
            )
        ]

        def yb_cfunc( ref, tu ) :
            html = tu.tohtml()
            [ assert_true(
                    r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, r in ybtext :
            yield self._test_execute, 'macro_yearsbefore', t, testcount, r, \
                  yb_cfunc
            testcount += 1

    @attr(type='anchor')
    def test_9_anchor( self ) :
        """Testing the Anchor() macro"""
        print "\nTesting the Anchor() macro"
        log.info( "Testing the Anchor() macro" )
        
        anchortext = [
            ( """ {{ Anchor( "Anchor name", "display text" ) }} """,
              [ 'name="Anchor name"', 'display text' ]
            )
        ]
        def anchor_cfunc( ref, tu ) :
            html = tu.tohtml()
            [ assert_true(
                    r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, r in anchortext :
            yield self._test_execute, 'macro_anchor', t, testcount, r, \
                  anchor_cfunc
            testcount += 1

    @attr(type='project')
    def test_A_project( self ) :
        """Testing the Project*() macros"""
        print "\nTesting the Project*() macro"
        log.info( "Testing the Project*() macro" )
        
        projecttext = [
            ( """ {{ Projectattributes() }} """, [] ),
            ( """ {{ Projectcompontents() }} """, [] ),
            ( """ {{ Projectdescription() }} """, [] ),
            ( """ {{ Projectteam() }} """, [] ),
            ( """ {{ Projectversions() }} """, [] ),
        ]
        def project_cfunc( ref, tu ) :
            html = tu.tohtml()
            [ assert_true(
                    r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, r in projecttext :
            yield self._test_execute, 'macro_project', t, testcount, r, \
                  project_cfunc
            testcount += 1

    @attr(type='htmlinwiki')
    def test_B_htmlinwiki( self ) :
        """Testing wiki with html"""
        print "\nTesting wiki with html"
        log.info( "Testing wiki with html" )

        testlist = [
            ( """ <div>hello world</div>""", [ '&lt;', '&gt;' ] )
        ]

        def html_cfunc( ref, tu ) :
            html = tu.tohtml()
            [ assert_true(
                r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, ref in testlist :
            yield self._test_execute, 'htmlinwiki', t, testcount, ref, \
                  html_cfunc
            testcount += 1

    @attr(type='stylesc')
    def test_C_styleshortcut( self ) :
        """Testing styleshortcut"""
        print "\nTesting styleshortcut"
        log.info( "Testing styleshortcut" )

        testlist = [
          ( """ ||{ {c;B;/1,solid,a;5|;|10} \n ||- \n || hello world \n ||}""",
            [ 'color: crimson', 'background-color: blue', 'hello world',
              'border : 1px solid aquamarine', 'margin : 5px', 'padding : 10px' ],
          ),
          ( """ ==={A;c;/2,dotted,b;|11;4|} hello world""",
            [ 'color: aquamarine', 'background-color: crimson', 'hello world',
              'border : 2px dotted blue', 'margin : 11px', 'padding : 4px' ],
          ),
          ( """ ''{/3,dashed,a;2|;|12;c;B} hello world ''""",
            [ 'color: crimson', 'background-color: blue', 'hello world',
              'border : 3px dashed aquamarine', 'margin : 2px', 'padding : 12px' ],
          ),
          ( """ |={c;B;/4,groove,a;5|;|10} heading1 |={c;B;/,solid,a;5|;|10} heading 2""",
            [ 'color: crimson', 'background-color: blue', 'hello world',
              'border : 4px groove aquamarine', 'margin : 5px', 'padding : 10px' ],
          ),
          ( """ *{5|;|10;c;B;/5,outset,a;} hello world""",
            [ 'color: crimson', 'background-color: blue', 'hello world',
              'border : 5px outset aquamarine', 'margin : 5px', 'padding : 10px' ],
          ),
        ]

        def sc_cfunc( ref, tu ) :
            html = tu.tohtml()
            [ assert_true(
                    r in html, 'Fail not found `%s` : %s ' % ( r, html )
              ) for r in ref ]

        testcount = 1
        for t, ref in testlist :
            yield self._test_execute, 'styleshortcuts', t, testcount, \
                  '', sc_cfunc
            testcount += 1


if __name__ == '__main__':
    unittest.main()
