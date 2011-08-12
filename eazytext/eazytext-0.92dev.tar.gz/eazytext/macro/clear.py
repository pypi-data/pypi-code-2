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

class Clear( Macro ) :
    """
    h3. Clear

    : Description :: 
        Styling macro to clear the DOM elements on both sides, warding off from
        floating effects. Accepts CSS styles for keyword arguments.
    : Example ::
        [<PRE {{ Clear() }} >]

    Positional arguments, //None//
    """
    tmpl = '<div class="etm-clear" style="%s"></div>'

    def __init__( self, *args, **kwargs ):
        self.style = constructstyle( kwargs )

    def __call__( self, argtext ):
        return eval( 'Clear( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ):
        return self.tmpl % self.style


# Register this plugin
gsm.registerUtility( Clear(), IEazyTextMacroFactory, 'Clear' )
