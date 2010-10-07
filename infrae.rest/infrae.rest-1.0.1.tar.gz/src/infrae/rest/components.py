# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: components.py 44853 2010-08-30 14:47:20Z sylvain $

from five import grok
from zExceptions import NotFound
from zope import component
from zope.publisher.browser import applySkin
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.traversing.namespace import view

from infrae.rest.interfaces import MethodNotAllowed, IRESTLayer

import simplejson

ALLOWED_REST_METHODS = ('GET', 'POST', 'HEAD', 'PUT',)


class REST(object):
    """A base REST component
    """
    grok.baseclass()
    grok.implements(IBrowserPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def response(self):
        return self.request.response

    def browserDefault(self, request):
        """Render the component using a method called the same way
        that the HTTP method name.
        """
        if request.method in ALLOWED_REST_METHODS:
            if hasattr(self, request.method):
                return self, (request.method,)
        raise MethodNotAllowed(request.method)

    def publishTraverse(self, request, name):
        """You can traverse to a method called the same way that the
        HTTP method name.
        """
        if name in ALLOWED_REST_METHODS and name == request.method:
            if hasattr(self, name):
                return getattr(self, name)
        raise NotFound(name)

    def json_response(self, result):
        """Encode a result as a JSON response.
        """
        self.response.setHeader('Content-Type', 'application/json')
        return simplejson.dumps(result)


class MethodNotAllowedView(grok.View):
    grok.context(MethodNotAllowed)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(405)

    def render(self):
        return u"Method not allowed"


class RESTNamespace(view):
    """Implement a namespace ++rest++.
    """

    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        applySkin(self.request, IRESTLayer)
        if name:
            view = component.queryMultiAdapter(
                (self.context, self.request), name=name)
            if view is None:
                raise NotFound(name)
            # Set view parent/name for security
            view.__name__ = name
            view.__parent__ = self.context
            return view
        return self.context
