# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source ode package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

import logging
import unittest
import os
import difflib                as diff
import random
from   random                 import choice, randint, shuffle

from   nose.plugins.attrib    import attr
from   nose.tools             import assert_equal, assert_raises, assert_true,\
                                     assert_false

from   eazytext                  import wiki_properties
from   eazytext.parser           import ETParser
import eazytext.test.testlib     as testlib
from   eazytext.test.testlib     import ETMARKUP, ETMARKUP_RE, \
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

tmpl            = """
{{{ %s
# {  'clear' : 'both',
#    'style' : 'border-bottom : 1px solid black; color : cyan;',
%s
%s
}}}
"""

def setUpModule() :
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
    
def tearDownModule() :
    testdir  = os.path.basename( os.path.dirname( __file__ ))
    testfile = os.path.basename( __file__ )
    log_mfooter( log, testdir, testfile )

class TestETextDumpsRandom( object ) :
    """Test cases to validate Extension random"""

    def _test_execute( self, type, testcontent, count, ref='', cfunc=None  ) :
        # Initialising the parser
        etparser     = ETParser( lex_optimize=True, yacc_optimize=False )

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

    def test_1_box( self ) :
        """Testing the Box() extension"""
        print "\nTesting the Box() extension"
        log.info( "Testing the Box() extension" )
        props = '\n'.join([ """# 'title'        : 'unit-testing box title',""",
                            """# 'titlestyle'   : 'color : magenta;',""",
                            """# 'contentstyle' : 'padding : 53px;',""",
                            """# }""" ])
        testlist = [
            ( tmpl % ( 'Box', props, 'Some wiki content' ),
              [ 'unit-testing box title', 'color : magenta', 'padding : 53', 
                'both', 'border-bottom : 1px solid black; color : cyan;'
              ]
            ),
        ]

        def box_cfunc( ref, tu ) :
            html= tu.tohtml()
            for r in ref :
                assert_true( r in html, 'Fail Box extension : %s ' % html )

        testcount = 1
        for t, r in testlist :
            yield self._test_execute, 'box_ext', t, testcount, r, \
                  box_cfunc
            testcount += 1

    def test_2_Code( self ) :
        """Testing the Code() extension"""
        print "\nTesting the Code() extension"
        log.info( "Testing the Code() extension" )
        props = """# }"""
        testlist = [
            ( tmpl % ( 'Code bash', props, 'ping google.com' ),
              [ 'both', 'border-bottom : 1px solid black; color : cyan;',
                'ping', 'google.com' ]
            ),
        ]

        def code_cfunc( ref, tu ) :
            html= tu.tohtml()
            for r in ref :
                assert_true( r in html, 'Fail Code extension : %s ' % html )

        testcount = 1
        for t, r in testlist :
            yield self._test_execute, 'code_ext', t, testcount, r, \
                  code_cfunc
            testcount += 1

    def test_3_Footnote( self ) :
        """Testing the Footnote() extension"""
        print "\nTesting the Footnote() extension"
        log.info( "Testing the Footnote() extension" )
        props = """# }"""
        testlist = [
            ( tmpl % ( 'Footnote Footnotes', props,
                       '1 Foot-note-1\n2 Foot-note-2' ),
              [ 'both', 'border-bottom : 1px solid black; color : cyan;',
                'name="1"', 'name="2"', 'Foot-note-1', 'Foot-note-2', ]
            ),
        ]

        def footnote_cfunc( ref, tu ) :
            html= tu.tohtml()
            for r in ref :
                assert_true( r in html, 'Fail Footnote extension : %s ' % html )

        testcount = 1
        for t,r in testlist :
            yield self._test_execute, 'footnote_ext', t, testcount, r, \
                  footnote_cfunc
            testcount += 1

    def test_4_HtmlExt( self ) :
        """Testing the HtmlExt() extension"""
        print "\nTesting the HtmlExt() extension"
        log.info( "Testing the HtmlExt() extension" )
        props = """# }"""
        testlist = [
            ( tmpl % ( 'HtmlExt', props, '<div>sometext</div>' ),
              [ 'both', 'border-bottom : 1px solid black; color : cyan;',
                '<div>sometext</div>' ]
            ),
            ( tmpl % ( 'HtmlExt', props, '' ),
              [ 'both', 'border-bottom : 1px solid black; color : cyan;', ]
            ),
        ]

        def html_cfunc( ref, tu ) :
            html= tu.tohtml()
            for r in ref :
                assert_true( r in html, 'Fail Html extension : %s ' % html )

        testcount = 1
        for t, r in testlist :
            yield self._test_execute, 'html_ext', t, testcount, r, \
                  html_cfunc
            testcount += 1

    def test_5_Nested( self ) :
        """Testing the Nested() extension"""
        print "\nTesting the Nested() extension"
        log.info( "Testing the Nested() extension" )
        props = """# }"""
        testlist = [
            ( tmpl % ( 'Nested', props, "''characters''" ),
              [ 'both', 'border-bottom : 1px solid black; color : cyan;',
                '<strong', '</strong>', 'characters' ]
            ),
        ]

        def nested_cfunc( ref, tu ) :
            html= tu.tohtml()
            for r in ref :
                assert_true( r in html, 'Fail Nested extension : %s ' % html )

        testcount = 1
        for t, r in testlist :
            yield self._test_execute, 'nested_ext', t, testcount, r, \
                  nested_cfunc
            testcount += 1
