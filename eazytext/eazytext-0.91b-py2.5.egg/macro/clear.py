# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

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

    template = '<div class="etm-clear" style="%s"></div>'

    def __init__( self, *args, **kwargs ) :
        self.style = constructstyle( kwargs )

    def tohtml( self ) :
        html = self.template % self.style
        return html
