# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   :
#   1. Add TOC with pos='inline'

from   random       import choice
from   copy         import copy, deepcopy

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

alphanum = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
random_word = lambda : ''.join([ choice(alphanum) for i in range(4) ])

#script = """
#<style type="text/css">
#    .dispnone { display : none; }
#</style>
#<script type="text/javascript">
#    dojo.addOnLoad(
#        function() {
#            var n_toc = dojo.query( 'div.toc' )[0];
#            var headdiv = n_toc.childNodes[0];
#            var toc_div = n_toc.childNodes[1];
#            dojo.connect( headdiv.childNodes[0], 'onclick',
#                function( e ) {
#                    if ( e.target.innerHTML == 'close' ) {
#                        dojo.toggleClass( toc_div, 'dispnone', true );
#                        e.target.innerHTML = 'show';
#                    } else if ( e.target.innerHTML == 'show' ) {
#                        dojo.toggleClass( toc_div, 'dispnone', false );
#                        e.target.innerHTML = 'close';
#                    }
#                    dojo.stopEvent( e );
#                }
#            );
#        }
#    );
#</script>
#"""

shorten = lambda s, m : s[:m] + (s[m:] and ' ...' or '' )

class Toc( Macro ) :
    """
    h3. Toc

    : Description ::
        Macro to generate Table of contents.  Accepts CSS styles for keyword
        arguments.
    : Example ::
        [<PRE {{ Toc() }} >]

    Positional arguments, //None//

    keyword argument,
    |= weight | optional, will be returned by on_posthtml() method
    |= topic  | optional, topic for table of contents
    |= maxheadlen | optional, number of characters to display for each title.
    """

    tmpl = '<div class="etm-toc" style="%s"> %s %s </div>'
    head_tmpl = '<div class="head"> %s %s </div>'
    topic_tmpl = '<div class="topic"> %s </div>'
    close_tmpl = '<div class="close">close</div>'
    tocul_tmpl = '<div class="toc"> %s </div>'

    tocli_tmpl = '<div class="%s"> %s </div>'
    toca_tmpl = '<a href="%s"> %s </a>'

    htags = [ 'h1', 'h2', 'h3', 'h4', 'h5', ]

    def __init__( self, **kwargs ) :
        weight = int( kwargs.pop( 'weight', '-1' ))
        self.maxheadlen = int(kwargs.pop( 'maxheadlen', 30 ))
        self.topic = kwargs.pop( 'topic', 'Table of Contents' )
        self.style  = constructstyle( kwargs )
        self.weight = weight == 0 and -1 or weight

    def tohtml( self ) :
        # Gotcha : cannot return a empty string since process_textcontent()
        # logic assumes that the translation fails. actually this macro is a
        # post html macro.
        return ' '

    def _maketoc( self, node ) :
        entries = []
        for n in node.getchildren() :
            if n.tag in self.htags :
                children  = n.getchildren()
                text = children[0].get('name'
                       ) if len(children) == 2 else children[1].get( 'name' )
                linktext = shorten( text, self.maxheadlen
                           ) if self.maxheadlen else text or ' '
                link = self.toca_tmpl % ( '#' + text, linktext )
                e = self.tocli_tmpl % ( n.tag, link )
                entries.append( e )
            entries.extend( self._maketoc( n ))
        return entries

    def on_posthtml( self ) :
        etparser = self.macronode.parser.etparser
        try :
            htmltree = lhtml.fromstring( etparser.html )
            topicdiv = self.topic_tmpl % self.topic
            closediv = self.close_tmpl
            headdiv = self.head_tmpl % ( closediv, topicdiv )
            entries = self._maketoc( htmltree )
            toc_div = self.tocul_tmpl % ''.join( entries )
            html = self.tmpl % (self.style, headdiv, toc_div)
        except :
            html = 'Unable to generate the TOC, ' + \
                            'Wiki page not properly formed ! <br></br>'
        return (self.weight, html)
