# -*- coding: utf-8 -*-

import grokcore.view as grok

from dolmen.file import INamedFile
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.security.interfaces import Unauthorized
from zope.security.management import checkPermission
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import ITraversable, TraversalError


class FilePublisher(grok.View):
    grok.name('file_publish')
    grok.context(INamedFile)

    def update(self):
        """Sets the response headers, according to the data infos.
        """
        if INamedFile.providedBy(self.context) and self.context.filename:
            self.response.setHeader(
                'Content-Disposition',
                'attachment; filename="%s"' % (
                    self.context.filename.encode('utf-8')))

        self.response.setHeader('Content-Type', self.context.contentType)
        self.response.setHeader('Content-Length', self.context.size)

    def render(self):
        return self.context.data


class FileTraverser(grok.MultiAdapter):
    grok.baseclass()
    grok.provides(ITraversable)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.response = request.response

    def get_file(self):
        raise NotImplementedError("Provide your own get_file method")

    def traverse(self, name, ignore=None):
        obj = self.get_file(name)
        if obj is not None:
            if not INamedFile.providedBy(obj):
                raise TraversalError('%s is not a valid INamedFile' % name)
            return getMultiAdapter((obj, self.request), name='file_publish')
        raise NotFound(self.context, name, self.request)


class DownloadTraverser(FileTraverser):
    grok.name('download')
    grok.adapts(Interface, IHTTPRequest)

    def get_file(self, name):
        if not checkPermission('zope.View', self.context):
            raise Unauthorized(name)
        return getattr(self.context, name, None)
