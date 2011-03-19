# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

class Images( Macro ) :
    """
    h3. Images

    : Description ::
        Embed Image galleries in the doc. 
        Accepts CSS styles for keyword arguments.

    Positional arguments,
    |= *args  | variable number of image sources (@src), one for each for image

    keyword argument,
    |= alt    | alternate text (@alt), that goes into each image
    |= height | optional, image height, applicable to all image's @height attr.
    |= width  | optional, image width, applicable to all image's @width attr.
    |= cols   | optional, number of image columns in the gallery, default is 3.
    """


    tmpl = '<table class="etm-images"> %s </table>'
    row_tmpl = '<tr> %s </tr>'
    cell_tmpl = '<td> %s </td>'
    img_tmpl = '<img %s %s src="%s" alt="%s" style="%s"> </img>'

    def __init__( self, *args, **kwargs ) :
        self.imgsources = args

        self.alt    = kwargs.pop( 'alt', '' )
        self.height = kwargs.pop( 'height', None )
        self.width  = kwargs.pop( 'width', None )
        self.cols   = int( kwargs.pop( 'cols', '3' ))
        
        self.style  = constructstyle( kwargs )

    def tohtml( self ) :
        hattr = self.height and ( 'height="%s"' % self.height ) or ''
        wattr = self.width and ( 'width="%s"' % self.width ) or ''

        imgsources = list(self.imgsources[:])
        rows = []
        while imgsources :
            cells = []
            for i in range( self.cols ) :
                if not imgsources :
                    break
                src = imgsources.pop( 0 )
                img = self.img_tmpl % ( hattr, wattr, src, self.alt, self.style )
                cell = self.cell_tmpl % img
                cells.append( cell )
            row = self.row_tmpl % '\n'.join( cells )
            rows.append( row )
        html = self.tmpl % '\n'.join( rows )
        return html
