# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Implementing the ProjectVersions macro"""

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
=== ProjectVersions

: Description ::
    Meant to be used in project front page, displays list of project versions

Default CSS styling,
> [<PRE %s >]

CSS styling accepted as optional keyword arguments
""" % css

class ProjectVersions( Macro ) :

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
                    { 'name' : 'projectvers',
                      'class': 'verdescr etmacro-projectversions',
                      'style' : self.style
                    }
                )
        e     = lhtml.Element( 'h3', { 'style' : "border-bottom : 1px solid cadetBlue; color: cadetBlue" })
        e.text= 'Versions'
        cntnr.append( e )
        versions = p and sorted( p.versions, key=lambda v : v.created_on ) or []
        for v in versions :
            e      = lhtml.Element( 'div', { 'style' : 'font-weight: bold' } ) 
            e.text = v.version_name or ' '  # Don't leave the text empty
            cntnr.append( e )
            e      = lhtml.Element( 'blockquote', {} )
            try :
                e.append( lhtml.fromstring( getattr( v, 'descriptionhtml', '<div> </div>' )))
            except :
                pass
            cntnr.append( e )
        return lhtml.tostring( cntnr )
