# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Implementing the ProjectDescription macro"""

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
=== ProjectDescription

: Description ::
    Meant to be used in project front page, displays project description

Default CSS styling,
> [<PRE %s >]

CSS styling accepted as optional keyword arguments
""" % css

template = """
<div>
    <div name="summary">
        <span style="font-weight: bold; color: gray;">Summary : </span>
        <em> %s </em>
    </div>
    <div name="desc">
        %s
    </div>
</div>
"""

class ProjectDescription( Macro ) :

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

        html= ''
        cntnr = lhtml.Element(
                    'div',
                    { 'name' : 'projectdesc',
                      'class' : 'projectdescription',
                      'style' : self.style
                    }
                )
        if p :
            cntnr.append( 
                lhtml.fromstring( template % \
                                ( p.summary, p.project_info.descriptionhtml )
                             )
            )
        return lhtml.tostring( cntnr )
