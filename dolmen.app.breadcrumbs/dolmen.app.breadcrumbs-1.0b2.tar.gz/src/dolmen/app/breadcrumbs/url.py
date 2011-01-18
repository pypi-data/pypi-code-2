# -*- coding: utf-8 -*-

import urllib
import grokcore.component as grok

from zope.component import getMultiAdapter
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.location.interfaces import ILocation
from zope.proxy import sameProxiedObjects
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser.absoluteurl import _insufficientContext, _safe
from zope.traversing.browser.interfaces import IAbsoluteURL


class DescriptiveAbsoluteURL(grok.MultiAdapter):
    grok.adapts(ILocation, IHTTPRequest)
    grok.implements(IAbsoluteURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        request = self.request

        # The application URL contains all the namespaces that are at the
        # beginning of the URL, such as skins, virtual host specifications and
        # so on.
        if (context is None
            or sameProxiedObjects(context, request.getVirtualHostRoot())):
            return request.getApplicationURL()

        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(_insufficientContext)

        url = str(getMultiAdapter((container, request), IAbsoluteURL))
        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError(_insufficientContext)

        if name:
            url += '/' + urllib.quote(name.encode('utf-8'), _safe)

        return url

    def __call__(self):
        return self.__str__()

    def naming(self):
        """Choose a display name for the current context.
        This method has been splitted out for convenient overriding.
        """
        name = getattr(self.context, '__name__', None)
        if name is None:
            raise TypeError(_insufficientContext)

        dc = IDCDescriptiveProperties(self.context, None)
        if dc is not None and dc.title:
            return name, dc.title

        return name, name

    def breadcrumbs(self):
        context = self.context
        request = self.request

        # We do this here do maintain the rule that we must be wrapped
        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(_insufficientContext)

        # We try to use the title instead of the name here.
        name, title = self.naming()

        if sameProxiedObjects(context, request.getVirtualHostRoot()) or \
               isinstance(context, Exception):
            return ({'name': title,
                     'url': self.request.getApplicationURL()}, )

        base = tuple(getMultiAdapter(
            (container, request), IAbsoluteURL).breadcrumbs())

        if name:
            url = "%s/%s" % (
                base[-1]['url'], urllib.quote(name.encode('utf-8'), _safe))
            base += (dict(name=title, url=url),)

        return base
