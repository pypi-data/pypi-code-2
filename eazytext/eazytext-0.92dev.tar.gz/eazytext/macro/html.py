# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   zope.component       import getGlobalSiteManager

from   eazytext.macro       import Macro
from   eazytext.interfaces  import IEazyTextMacroFactory

gsm = getGlobalSiteManager()

class Html( Macro ) :
    """
    h3. Html

    : Description ::
        Embed HTML text within wiki doc. Try to use ''~[< ... ~>]'' markup
        first, if advanced styling is required for the embedded HTML text,
        then this macro can come in handy.
    : Example ::
        [<PRE {{ Html( '<b>hello world</b>' ) }} >]

    Positional arguments,
    |= html | HTML text
    """

    def __init__( self, html='' ) :
        self.htmltext  = html

    def __call__( self, argtext ):
        return eval( 'Html( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        return self.htmltext


# Register this plugin
gsm.registerUtility( Html(), IEazyTextMacroFactory, 'Html' )
