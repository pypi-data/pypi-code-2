# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   :
#   CSS styling is currently using zeta.

from   eazytext.macro  import Macro
from   eazytext        import split_style, constructstyle, lhtml

css = {
    'padding'            : '5px',
    'background'         : '#e5ecf9',
    'margin'             : '10px 0px 10px 5px'
}

wikidoc = """
=== ProjectAttributes

: Description ::
    Meant to be used in project front page, displays project attributes, like
    admin, mailinglist, license etc ...

Default CSS styling,
> [<PRE %s >]

CSS styling accepted as optional keyword arguments
""" % css

template = """
<div>
    <div style="display: table">
        <div style="display: table-row">
            <div  class="ralign p5 fntbold" style="width: 8em; display: table-cell; border: none">admin-email :</div>
            <div  class="p5" style="display: table-cell; border: none">%s </div>
        </div>
        <div style="display: table-row">
            <div class="ralign p5 fntbold" style="width: 8em; display: table-cell; border: none;">license : </div>
            <div class="p5" style="display: table-cell; border: none"> %s </div>
        </div>
        <div style="display: table-row">
            <div class="ralign p5 fntbold" style="width: 8em; display: table-cell; border: none;">mailing-lists : </div>
            <div class="p5" style="display: table-cell; border: none"> %s </div>
        </div>
        <div style="display: table-row">
            <div class="ralign p5 fntbold" style="width: 8em; display: table-cell; border: none;">irc-channels : </div>
            <div class="p5" style="display: table-cell; border: none"> %s </div>
        </div>
    </div>
</div>
"""

class ProjectAttributes( Macro ) :

    def __init__( self, *args, **kwargs ) :
        self.project = args and args[0]
        self.style   = constructstyle( kwargs, defcss=css )

    def tohtml( self ) :
        etp = self.macronode.parser.etparser
        app = etp.app
        etp.dynamictext = True

        try :   # To handle test cases.
            p = getattr( app.c, 'project', None )
        except :
            p = None
        if self.project :
            p = app.projcomp.get_project( unicode(self.project ))

        cntnr = lhtml.Element(
                    'div',
                    { 'name' : 'projectattrs',
                      'style' : self.style,
                      'class' : 'etmacro-projectattributes'
                    }
                )
        if p :
            cntnr.append(
                lhtml.fromstring(
                    template % \
                        ( p.admin_email, p.license and p.license.licensename,
                          ', '.join([ m.mailing_list for m in p.mailinglists ]),
                          ', '.join([ m.ircchannel for m in p.ircchannels ]),
                        )
                )
            )
        return lhtml.tostring( cntnr )
