# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none
#   1. Unit test case for this extension.

from   eazytext.extension   import Extension
from   eazytext             import split_style, constructstyle, lhtml

doc = """
=== Nested

: Description ::
    Nest another EazyText document / text within the current
    document. Property key-value pairs accepts CSS styling attributes.
"""


class Nested( Extension ) :

    tmpl = '<div class="etext-nested"> %s </div>'
    
    def __init__( self, props, nowiki, *args ) :
        self.nowiki = nowiki
        self.style = constructstyle( props )

    def tohtml( self ) :
        from   eazytext.parser import ETParser

        if self.nowiki :
            etparser = ETParser(
                            nested=True,
                            style=self.style,
                            skin=None,
                            lex_optimize=False,
                            yacc_optimize=False,
                       )
            tu = etparser.parse( self.nowiki, debuglevel=0 )
            try :
                html = self.tmpl % ( tu.tohtml() )
            except :
                html = self.tmpl % ''
        return html

Nested._doc = doc
