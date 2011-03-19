# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None


from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

class Anchor( Macro ) :
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

    template = '<a class="etm-anchor" name="%s" style="%s"> %s </a>'

    def __init__( self, *args, **kwargs ) :
        args = list( args )
        self.anchor = args and args.pop( 0 ) or ''
        self.text = args and args.pop( 0 ) or '&#167;'
        self.style = constructstyle( kwargs )

    def tohtml( self ) :
        html = self.template % ( self.anchor, self.style, self.text )
        return html
