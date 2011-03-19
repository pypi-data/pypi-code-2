# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Change the mapping if the style shortcut for color need to be customized"""

import re

fgcolors = {
    'a'     : 'aquamarine',
    'b'     : 'blue',
    'c'     : 'crimson',
    'd'     : '',
    'e'     : '',
    'f'     : 'fuchsia',
    'g'     : 'green',
    'h'     : '',
    'i'     : 'indigo',
    'j'     : '',
    'k'     : 'khaki',
    'l'     : 'lavender',
    'm'     : 'maroon',
    'n'     : 'navy',
    'o'     : 'orange',
    'p'     : 'pink',
    'q'     : '',
    'r'     : 'red',
    's'     : 'skyBlue',
    't'     : 'teal',
    'u'     : '',
    'v'     : 'violet',
    'w'     : 'white',
    'x'     : '',
    'y'     : 'yellow',
    'z'     : '',
}

bgcolors = {
    'A'     : 'aquamarine',
    'B'     : 'blue',
    'C'     : '',
    'D'     : '',
    'E'     : '',
    'F'     : 'fuchsia',
    'G'     : 'green',
    'H'     : '',
    'I'     : 'indigo',
    'J'     : '',
    'K'     : 'khaki',
    'L'     : 'lavender',
    'M'     : 'maroon',
    'N'     : 'navy',
    'O'     : 'orange',
    'P'     : 'pink',
    'Q'     : '',
    'R'     : 'red',
    'S'     : 'skyBlue',
    'T'     : 'teal',
    'U'     : '',
    'V'     : 'violet',
    'W'     : 'white',
    'X'     : '',
    'Y'     : 'yellow',
    'Z'     : '',
}

def style_color( m ) :
    return 'color: %s;' % fgcolors[m]
fg_pattern = ( re.compile( r'^[a-z]$' ), style_color )

def style_background( m ) :
    return 'background-color: %s;' % bgcolors[m]
bg_pattern = ( re.compile( r'^[A-Z]$' ), style_background )

def style_border( m ) :
    w, style, color = m[1:].split( ',' )
    color = fgcolors[color]
    return 'border : %spx %s %s;' % ( w, style, color )
_r = r'^/[0-9]+,(dotted|dashed|solid|double|groove|ridge|inset|outset),[a-z]$'
border_pattern = ( re.compile( _r ), style_border )

def style_margin( m ) :
    return 'margin : %spx' % m[:-1]
margin_pattern = ( re.compile( r'^[0-9]+\|$' ), style_margin )

def style_padding( m ) :
    return 'padding : %spx' % m[1:]
padding_pattern = ( re.compile( r'^\|[0-9]+$' ), style_padding )

stylematcher = [ fg_pattern, bg_pattern, border_pattern, margin_pattern,
                 padding_pattern ]

def styleparser( stylemarkups ) :
    """Parse the text for style markup and convert them into html style
    attribute values"""
    stylemarkups = stylemarkups.strip('{}')
    props = [ prop.strip( ' \t' ) for prop in stylemarkups.split( ';' ) ]
    styleprops   = []
    for prop in props :
        for regex, func in stylematcher :
            if regex.match( prop ) :
                styleprops.append( func( prop ))
                break
        else :
            styleprops.append( prop )
    return '; '.join( styleprops )


