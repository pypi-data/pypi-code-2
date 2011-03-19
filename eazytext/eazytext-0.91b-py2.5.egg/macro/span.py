# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

class Span( Macro ) :
    """
    h3. Span

    : Description ::
        Create a span element. Try using ~``...~`` markup to generate span
        elements, if advanced styling is required, this macro can come in handy.
        Accepts CSS styles for keyword arguments.
    : Example ::
        [<PRE {{ Span( 'hello world' ) }} >]

    Positional arguments,
    |= text   | optional, text for the span element
    """

    tmpl = '<span class="etm-span" style="%s"> %s </span>'

    def __init__( self, *args, **kwargs ) :
        self.text = len(args) > 0 and args[0] or ''
        self.style = constructstyle( kwargs )

    def tohtml( self ) :
        html = self.tmpl % ( self.style, self.text )
        return html
