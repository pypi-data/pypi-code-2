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
from   eazytext.lib         import constructstyle

gsm = getGlobalSiteManager()

class Anchor( Macro ):
    """
    h3. Anchor

    : Description ::
        Create an anchor in the document which can be referenced else-wehere.
        Accepts CSS styles for keyword arguments.
    : Example ::
        [<PRE {{ Anchor( 'anchorname', 'display-text' ) }} >]

    Positional arguments,

    |= anchor | anchor name as fragment, goes under @name attribute
    |= text   | optional, text to be display at the anchor
    """
    tmpl = '<a class="etm-anchor" name="%s" style="%s"> %s </a>'

    def __init__( self, *args, **kwargs ):
        args = list( args )
        self.anchor = args and args.pop( 0 ) or ''
        self.text = args and args.pop( 0 ) or '&#167;'
        self.style = constructstyle( kwargs )

    def __call__( self, argtext ):
        return eval( 'Anchor( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        return self.tmpl % ( self.anchor, self.style, self.text )

# Register this plugin
gsm.registerUtility( Anchor(), IEazyTextMacroFactory, 'Anchor' )
