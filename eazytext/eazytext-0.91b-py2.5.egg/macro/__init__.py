"""
h3. EazyText Macro framework

Macros are direct function calls that can be made from wiki text into the wiki
engine, provided, there is a macro by that name available. Most probably the
macro will return a html content, which will be used to replace the macro
call. More specifically the macro call will be directly evaluated as python
code and thus follows all the function calling rules and conventions of
python. 

To expound it further, let us take a specific example of ''YearsBefore''
Macro, which computes the time elapsed from a given (month,day,year) and
composes a string like "2 years 2 months before",

Definition of YearsBefore macro,
> [<PRE YearsBefore( template, fromyear, frommonth=1, fromday=1, **kwargs ) >]

''A small primer on python function calls'',
* Arguments to python functions are of two types, positional and keyword. Other
  types of argument passing are not of concern here.
* Position arguments are specified first in a function call, where the first
  passed parameter is recieved as the first argument, second passed parameter
  is recieved as the second argument and so on. All positional parameters
  are mandatory.
* Keyword arguments are received next. Keyword arguments also carry a
  default value, if in case it is not passed.

With this in mind, we will try to decipher ''YearsBefore'' macro

* ''YearsBefore'', is the name of the macro function.
* ''template'', is the first mandatory positional argument providing the
  template of output string.
* ''fromyear'', is the second mandatory positional argument, specifying the
  year.
* ''frommonth'', is optional keyword argument, specifying the month.
* ''fromday'', is option keyword argument, specifying the day.
* ''kwargs'', most of the macro functions have this last arguments to accept a
  variable number of keyword arguments. One use case for this is to
  pass styling attributes.

Use case,
> [<PRE started this activity and running this for {{ YearsBefore('past %s', '2008') }} >]

> started this activity and running this for {{ YearsBefore('past %s', '2008') }}

=== Styling paramters

To get the desired CSS styling for the element returned by macro, pass in the styling
attributes as keyword arguments, like,

> [<PRE started this activity and running this for 
  {{ YearsBefore('past %s', '2008', color="red" ) }} >]

> started this activity and running this for 
> {{ YearsBefore('past %s', '2008', color="red" ) }}

Note that, the attribute name is represented as local variable name inside the
macro function. If you are expert CSS author, you will know that there are
CSS-style attribute-names like ''font-size'', ''font-weight'' which are not
valid variables, so, style attribute-names which contain a ''hypen''
cannot be passed as a keyword argument. As an alternative, there is a special
keyword argument (to all macro functions) by name ''style'', which directly
accepts ''semicolon (;)'' seperated style attributes, like,

> [<PRE started this activity and running this for 
   {{ YearsBefore('past %s', '2008', color="red", style="font-weight: bold; font-size: 200%" ) }} >]

> started this activity and running this for 
> {{ YearsBefore('past %s', '2008', color="red", style="font-weight: bold; font-size: 200%" ) }}

"""

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.


# -*- coding: utf-8 -*-

# Gotcha : none
#   1. While testing EazyText, make sure that the exception is not re-raised
#      for `eval()` call.
# Notes  : none
# Todo   : 
#   1. Test case for yearsbefore macro

import os, sys
from   os.path     import splitext, dirname

from   paste.util.import_string  import import_module, eval_import

class Macro( object ) :
    """
    Base Macro class that should be used to derive EazyText Macro classes
    The following attributes are available for the Macro() object.
      * macronode        passed while instantiating, provides the Macro instance
      * macronode.parser PLY Yacc parser
      * parser.etparser  ETParser() object
      * etparser.tu      Translation Unit for the parsed text
      * etparser.text    Raw wiki text.
      * etparser.pptext  Preprocessed wiki text.
      * etparser.html    Converted HTML code from Wiki text
    """
    
    def __init__( self, *args, **kwargs ) :
        pass

    def on_parse( self,  ) :
        """Will be called after parsing the extension text"""
        pass

    def on_prehtml( self,  ) :
        """Will be called before calling tohtml() method"""
        pass

    def tohtml( self ) :
        """HTML content to replace the macro text"""
        return ''

    def on_posthtml( self,  ) :
        """Will be called afater calling tohtml() method"""
        pass


macrolist = {}
def loadmacros( dirname ) :
    global macrolist
    sys.path.insert( 0, dirname )
    plugin_files = list(set([ 
                        splitext(f)[0]
                        for f in os.listdir(dirname)
                        if f[0] != '.' and f != '__init__.py' 
                   ]))
    for p in plugin_files :
        m = eval_import( p )
        for attr in dir(m) :
            obj = m.__dict__[attr]
            try :
                if issubclass( obj, Macro ) :
                    globals()[obj.__name__] = obj
                    macrolist.setdefault( obj.__name__, obj )
            except:
                pass
    sys.path.remove(dirname)

def build_macro( macronode, macro ) :
    """Parse the macro text, like,
        {{ Macroname( arg1, arg2, kwarg1=value1, kwarg2=value2 ) }}
    To function name, *args and **kwargs
    """
    try :
        o = eval( macro[2:-2] )
    except :
        o = Macro()
        if macronode.parser.etparser.debug : raise

    if not isinstance( o, Macro ) :
        o = Macro()

    etparser = macronode.parser.etparser

    # Register macro-node
    o.macronode = macronode     # Backreference to parser AST node
    etparser.regmacro( o )      # Register macro with the parser
    o.on_parse()                # Callback on_parse()
    return o

loadmacros( dirname( __file__ ) )
