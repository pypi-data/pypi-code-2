# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Roberto Longobardi - seccanj@gmail.com, Marco Cipriani
#

from genshi.builder import tag

from trac.core import *
from trac.mimeview import Context
from trac.web.chrome import ITemplateProvider, INavigationContributor
                            
class TicketTreeTemplateProvider(Component):
    """Provides templates and static resources for the TicketTree plugin."""

    implements(ITemplateProvider)

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        from pkg_resources import resource_filename
        return [('tickettree', resource_filename('tickettree', 'htdocs'))]

    def get_templates_dirs(self):
        """
        Return the absolute path of the directory containing the provided
        Genshi templates.
        """
        return []

        
class TicketTreeSystem(Component):
    """Implements the Ticket Tree tab."""

    implements(INavigationContributor)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        if 'TICKET_VIEW' in req.perm:
            return 'tickettree'

    def get_navigation_items(self, req):
        if 'TICKET_VIEW' in req.perm:
            yield ('mainnav', 'tickettree',
                tag.a("Ticket Tree", href=req.href.wiki()+'/TicketTree', accesskey='T'))

