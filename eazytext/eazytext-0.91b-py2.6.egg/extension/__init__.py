# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""
h3. EazyText Extensions

EazyText Extension is a plugin framework to extend wiki engine itself. One
can define new markups, text formats etc ... and integrate it with EazyText as
an extension.

h3. Extension Framework

Extented wiki text can be added into the main document by enclosing them within
triple curly braces '' ~{~{{ ... ~}~}} ''. Everything between the curly braces
are passed directly to the extension module, which, in most of the cases will
return a translated HTML text. The general format while using a wiki extension
is,

> ~{~{~{''extension-name'' //space seperated parameter-strings//
> # {
> # ''property-name'' : //value//
> # ''property-name'' : //value//
> # ...
> # }
> 
> ''wiki-text ...''
> ~}~}~}

* ''extension-name'', should be one of the valid extensions.
* ''parameter-strings'', string values that will be passed as parameters.
* ''property-name'', property name can be a property accepted by the extension
  module or can be CSS property. Note that, the entire property block should
  be marked by a beginning ''hash (#)''
* ''wiki-text'', the actual text that get passed on to the extension class.
"""

# -*- coding: utf-8 -*-

# Gotcha : None
#   1. While testing EazyText, make sure that the exception is not re-raised
#      for `eval()` call.
# Notes  : None
# Todo   : None

import os, sys
from   os.path     import splitext, dirname

class Extension( object ) :
    """Base Extension class that should be used to derive
    EazyText extension / nowiki classes.
    The following attributes are available for the Extension() object.
      *  extnode        passed while instantiating, provides the Extention
                        instance
      *  extnode.parser ETParser() object
      *  parser.tu      Translation Unit for the parsed text
      *  parser.text    Raw wiki text.
      *  parser.pptext  Preprocessed wiki text.
      *  parser.html    Converted HTML code from Wiki text
    """
    
    def __init__( self, props, nowiki ) :
        pass

    def on_parse( self,  ) :
        """Will be called after parsing the extension text"""
        pass

    def on_prehtml( self,  ) :
        """Will be called before calling tohtml() method"""
        pass

    def tohtml( self ) :
        """HTML content to replace the nowiki text"""
        return ''

    def on_posthtml( self,  ) :
        """Will be called afater calling tohtml() method"""
        pass


from eazytext                    import split_style, constructstyle

extlist = {}
def loadextensions( dirname ) :
    global extlist
    sys.path.insert( 0, dirname )
    plugin_files = list(set([ 
                        splitext(f)[0]
                        for f in os.listdir(dirname)
                        if f[0] != '.' and f != '__init__.py' 
                   ]))
    for p in plugin_files :
        m = __import__( p )
        for attr in dir(m) :
            obj = m.__dict__[attr]
            try :
                if issubclass( obj, Extension ) :
                    globals()[obj.__name__] = obj
                    extlist.setdefault( obj.__name__, obj )
            except :
                pass
    sys.path.remove(dirname)

def build_ext( extnode, nowiki ) :
    """Parse the nowiki text, like,
        {{{ ExtensionName
        # property dictionary
        # ..
        # ..
        ....
        }}}
    To function name, *args and **kwargs
    """
    props = []
    nowikilines = nowiki.split( '\n' )
    for i in range( len(nowikilines) ) :
        if len(nowikilines[i]) and nowikilines[i][0] == '#' :
            props.append( nowikilines[i][1:] )
            continue
        break;
    nowiki = '\n'.join( nowikilines[i:] )

    try :
        props = props and eval( ''.join( props ) ) or {}
    except :
        props = {}

    try :
        xwiki = extnode.xwikiname
        args = [ props, nowiki ] + extnode.xparams
        o  = globals()[extnode.xwikiname]( *args )
    except :
        o = Extension( {}, nowiki )
        if extnode.parser.etparser.debug : raise

    if not isinstance( o, Extension ) :
        o = Extension( {}, nowiki )

    etparser = extnode.parser.etparser

    o.extnode = extnode     # Backreference to parser AST node
    extnode.parser.etparser.regext( o ) # Register macro with the parser
    o.on_parse()                # Callback on_parse()
    return o

loadextensions( dirname( __file__ ) )
