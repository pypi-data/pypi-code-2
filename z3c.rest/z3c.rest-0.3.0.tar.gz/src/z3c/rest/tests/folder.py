##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test REST view for folders.

$Id: folder.py 82045 2007-11-30 11:40:12Z srichter $
"""
import lxml.etree
from z3c.rest import rest
from zope.app.folder import folder
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publication.http import MethodNotAllowed
from zope.dublincore.interfaces import IZopeDublinCore

class FolderAPI(rest.RESTView):
    """A simple REST view for folders."""

    template = ViewPageTemplateFile("folder.pt")

    def __init__(self, context, request):
        super(FolderAPI, self).__init__(context, request)
        for param in ('noitems', 'notitle'):
            if 'HTTP_DEMO_' + param.upper() in self.request:
                self.request.parameters[param] = 1

    def GET(self):
        return self.template()

    def POST(self):
        tree = lxml.etree.parse(self.request.bodyStream)
        title = tree.find('title').text
        dc = IZopeDublinCore(self.context)
        dc.title = unicode(title)

    # For existing resources, PUT pretty much behaves like POST
    PUT = POST

    def NullPUT(self, nullResource):
        name = nullResource.name
        self.context[name] = folder.Folder()
        return self.context[name]

    def DELETE(self):
        container = self.context.__parent__
        if container is None:
            raise MethodNotAllowed(self.context, self.request)
        del container[self.context.__name__]
