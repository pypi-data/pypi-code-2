# zope integration for hurry.resource
from grokcore import component as grok

from zope import interface
from zope import component
from zope.component.hooks import getSite
import zope.security.management
from zope.publisher.interfaces import IRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.publisher.browser import BrowserRequest, BrowserResponse, isHTML
from zope.app.publication.interfaces import IBrowserRequestFactory

from hurry.resource import NeededInclusions, render_topbottom_into_html
from hurry.resource.interfaces import (
    ICurrentNeededInclusions, ILibrary, ILibraryUrl)


class CurrentNeededInclusions(grok.GlobalUtility):
    grok.implements(ICurrentNeededInclusions)
    grok.provides(ICurrentNeededInclusions)

    def __call__(self):
        try:
            request = getRequest()
        except NoRequestError:
            # in some situations no request is set up
            # to let 'need()' happen freely in places where
            # no request is available (such as tests) we will
            # silently assume that this is all right and return
            # an empty NeededInclusions
            return NeededInclusions()

        if not hasattr(request, 'hurry_resource_needed'):
            request.hurry_resource_needed = NeededInclusions()
        return request.hurry_resource_needed


@grok.adapter(ILibrary)
@grok.implementer(ILibraryUrl)
def library_url(library):
    request = getRequest()
    return str(component.getMultiAdapter((getSite(), request),
                                         IAbsoluteURL)) + '/@@/' + library.name


class Request(BrowserRequest):
    interface.classProvides(IBrowserRequestFactory)

    def _createResponse(self):
        return Response()


class Response(BrowserResponse):
    def _implicitResult(self, body):
        content_type = self.getHeader('content-type')
        if content_type is None:
            if isHTML(body):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            self.setHeader('x-content-type-warning', 'guessed from content')
            self.setHeader('content-type', content_type)

        # check the content type disregarding parameters and case
        if content_type and content_type.split(';', 1)[0].lower() in (
            'text/html', 'text/xml'):
            # act on HTML and XML content only!
            body = render_topbottom_into_html(body)

        return super(Response, self)._implicitResult(body)


class NoRequestError(Exception):
    pass


def getRequest():
    try:
        i = zope.security.management.getInteraction()  # raises NoInteraction
    except zope.security.interfaces.NoInteraction:
        raise NoRequestError()

    for p in i.participations:
        if IRequest.providedBy(p):
            return p

    raise NoRequestError()
