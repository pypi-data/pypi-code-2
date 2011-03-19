# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None


from   eazytext.macro  import Macro
from   eazytext        import lhtml

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
        self.html  = html

    def tohtml( self ) :
        return self.html
