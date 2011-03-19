# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

class Image( Macro ) :
    """
    h3. Image

    : Description ::
        Embed Images in the doc. Try to use ''Link markup'' to embed images, if
        advanced styling is required, this macro can come in handy.
        Accepts CSS styles for keyword arguments.
    : Example ::
        [<PRE {{ Image( '/photo.jpg' ) }} >]

    Positional arguments,
    |= src    | source-url for image, goes into @src attribute
    |= alt    | alternate text, goes into @alt attribute

    keyword argument,
    |= height | optional, image height, goes into @height attribute
    |= width  | optional, image width, goes into @width attribute
    |= href   | optional, href, to convert the image into a hyper-link
    """


    template = '<img class="etm-image" ' + \
               '%s %s src="%s" alt="%s" style="%s"> </img>'

    def __init__( self, src, alt, **kwargs ) :
        self.src = src
        self.alt = alt
        self.height = kwargs.pop( 'height', None )
        self.width = kwargs.pop( 'width', None )
        self.href = kwargs.pop( 'href', '' )
        self.style = constructstyle( kwargs )

    def tohtml( self ) :
        hattr = self.height and ( 'height="%s"' % self.height ) or ''
        wattr = self.width and ( 'width="%s"' % self.width ) or ''
        img = self.template % ( hattr, wattr, self.src, self.alt, self.style )
        # If the image is a link, enclose it with a 'anchor' dom-element.
        if self.href :
            href = lhtml.Element( 'a', { 'href' : self.href } )
            href.append( lhtml.fromstring( img ))
            html = lhtml.tostring( href )
        else :
            html = img
        return html
