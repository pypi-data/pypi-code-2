# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Implementing the ProjectComponents macro"""

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

css = {
    'padding'   : '0px',
    'border'    : '0px',
}

wikidoc = """
=== ProjectComponents

: Description ::
    Meant to be used in project front page, displays list of project components

Default CSS styling,
> [<PRE %s >]

CSS styling accepted as optional keyword arguments
""" % css

ct_template = """
<div>
    <span style="font-weight: bold">%s </span>
    owned by
    <a href="%s">%s </a>
</div>
"""

class ProjectComponents( Macro ) :

    def __init__( self, *args, **kwargs ) :
        self.project = args and args[0]
        self.style   = constructstyle( kwargs, defcss=css )

    def tohtml( self ) :
        etp = self.macronode.parser.etparser
        app = etp.app
        etp.dynamictext = True

        try :   # To handle test cases.
            p   = getattr( app.c, 'project', None )
        except :
            p   = None
        if self.project :
            p = app.projcomp.get_project( unicode(self.project ))

        cntnr = lhtml.Element(
                    'div',
                    { 'name' : 'projectcomps',
                      'class' : 'etmacro-projectcomponents compdescr',
                      'style' : self.style
                    }
                )
        e = lhtml.Element( 'h3', { 'style' : "border-bottom : 1px solid cadetBlue; color: cadetBlue" })
        e.text= 'Components'
        cntnr.append( e )
        components = p and sorted( p.components, key=lambda c : c.created_on ) or []
        for c in components :
            owner  = c.owner.username
            e      = lhtml.fromstring( ct_template % ( c.componentname,
                                                    app.h.url_foruser( owner ),
                                                    owner
                                                  )
                                  )
            cntnr.append( e )
            e      = lhtml.Element( 'blockquote', {} )
            try :
                e.append( lhtml.fromstring( getattr( c, 'descriptionhtml', '<div> </div>' )))
            except :
                pass
            cntnr.append( e )
        return lhtml.tostring( cntnr )
