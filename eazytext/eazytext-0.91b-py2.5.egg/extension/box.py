# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none
#   1. Unit test case for this extension.

from   eazytext.extension   import Extension
from   eazytext             import split_style, lhtml

doc = """
h3. Box

: Description ::
    Generate a box with title and content. Text within the curly braces
    will be interpreted as the content and can contain EazyText text as well.
    If title text is provided, then the extension can take parameter
    ''hide'' which can be used to shrink/expand box content.

Property key-value pairs accepts CSS styling attributes and other special
attributes like,

|= title        | optional, title string
|= titlestyle   | optional, title style string in CSS style format
|= contentstyle | optional, content style string in CSS style format

''Example''

> [<PRE{{{ Box hide
 #{
 # 'title' : 'Building Mnesia Database',
 # 'titlestyle' : 'color: brown;',
 # 'contentstyle' : 'color: gray;',
 # 'border' : '1px solid gray',
 # 'style' : { 'margin' : '10px', 'padding' : '10px' },
 #}
 This chapter details the basic steps involved when designing a Mnesia
 database and the programming constructs which make different solutions
 available to the programmer. The chapter includes the following sections,
 
 * defining a schema
 * the datamodel
 * starting Mnesia
 * creating new tables.
}}} >]

{{{ Box hide
#{
# 'title' : 'Building Mnesia Database',
# 'titlestyle' : 'color: brown;',
# 'contentstyle' : 'color: gray;',
# 'border' : '1px solid gray',
# 'style' : { 'margin' : '10px', 'padding' : '10px' },
#}

This chapter details the basic steps involved when designing a Mnesia database
and the programming constructs which make different solutions available to the
programmer. The chapter includes the following sections:

* defining a schema
* the datamodel
* starting Mnesia
* creating new tables.

}}}

"""

tmpl = """
<div class="etext-box" style="%s">
    <div class="boxtitle" style="%s">
    %s %s
    </div>
    <div class="boxcont" style="%s">%s</div>
</div>
"""

spantmpl = """
<span class="boxhide"> hide</span>
<span class="boxshow"> show</span>
"""

class Box( Extension ) :
    _doc = doc

    def __init__( self, props, nowiki, *args ) :
        self.nowiki = nowiki
        self.title = props.pop( 'title', '' )
        boxstyle = props.pop( 'style', {} )
        titlestyle = props.pop( 'titlestyle', {} )
        contentstyle = props.pop( 'contentstyle', '' )

        d_style, s_style = split_style( boxstyle )
        self.style = s_style
        self.css = {}
        self.css.update( props )
        self.css.update( d_style )

        d_style, s_style = split_style( titlestyle )
        self.titlestyle = s_style
        self.title_css = {}
        self.title_css.update( d_style )

        d_style, s_style  = split_style( contentstyle )
        self.contentstyle = s_style
        self.cont_css = {}
        self.cont_css.update( d_style )

        self.hide = 'hide' in args

    def tohtml( self ) :
        from   eazytext.parser import ETParser

        fn = lambda (k, v) : '%s : %s' % (k,v)

        boxstyle = '; '.join(map( fn, self.css.items() ))
        if self.style :
            boxstyle += '; %s ;' % self.style

        titlestyle = '; '.join(map( fn, self.title_css.items() ))
        if self.titlestyle  :
            titlestyle += '; %s ;' % self.titlestyle

        contstyle = '; '.join(map( fn, self.cont_css.items() ))
        if self.contentstyle :
            contstyle += '; %s ;' % self.contentstyle

        self.nowiki_h = ''
        if self.nowiki :
            etparser = ETParser(
                             skin=None,
                             nested=True,
                             lex_optimize=False,
                             yacc_optimize=False,
                       )
            tu = etparser.parse( self.nowiki, debuglevel=0 )
            self.nowiki_h = tu.tohtml()

        if self.title :
            html = tmpl % ( boxstyle, titlestyle, self.title, spantmpl,
                            contstyle, self.nowiki_h )
        else :
            html = tmpl % ( boxstyle, titlestyle, self.title, '',
                            contstyle, self.nowiki_h )
        return html

