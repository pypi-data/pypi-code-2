"""This package contains the ``Main`` view, which is the entry point
into your skin.  The equivalent to Plone's 'main template' can be found
at ``templates/main.pt``
"""
from Acquisition import aq_inner
from zope import interface
from zope import component
from zExceptions import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from OFS.Image import File
from Products.ATContentTypes.atct import ATCTFileContent
import plone.app.layout.viewlets.common
import plone.postpublicationhook.interfaces

from collective.skinny.base import render_viewlet
from collective.skinny.base import BaseView
from collective.skinny.interfaces import IPublicLayer, IPublicLayerOK

import collective.skinny.content

class MyNavigation(BaseView):
    """An example of a simple navigation implementation that simply
    reuses Plone's GlobalSectionViewlet and the PathBarViewlet.
    """
    def __call__(self):
        html = render_viewlet(
            plone.app.layout.viewlets.common.GlobalSectionsViewlet, self)
        html += render_viewlet( 
            plone.app.layout.viewlets.common.PathBarViewlet, self)
        return html

class Main(BaseView):
    
    template = ViewPageTemplateFile('templates/main.pt')

    media_content_inline = True

    # Part definitions:

    # When in your template, you say ``view/render_content``, we'll
    # first look into the parts dict to see if you have a part
    # registered here.  Otherwise, we'll fall back to looking up a
    # template in the templates directory.  That is, you can put
    # ``spam.pt`` into your templates directly and use it via
    # ``view/render_spam`` without the need of registering anything
    # here:
    parts = {
        'content': collective.skinny.content.Registry,
        'navigation': MyNavigation,
        }
    
    def __call__(self):
        context = self.context
        
        # Mark the request as OK; it's gone through us:
        interface.alsoProvides(self.request, IPublicLayerOK)

        # Return media objects inline:
        if (self.media_content_inline and
            isinstance(context, (File, ATCTFileContent))):
            return context.index_html(self.request, self.request.response)

        return self.template()

    def language(self):
        """Return two letter code of context's language, useful with
        <html> tag.
        """
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return (aq_inner(self.context).Language() or
                portal_state.default_language())

@component.adapter(interface.Interface,
                   plone.postpublicationhook.interfaces.IAfterPublicationEvent)
def dont_leak(object, event):
    request = event.request

    # Allow any non html resources:
    headers = request.response.headers
    if not headers.get('content-type', '').startswith('text/html'):
        return

    # Everything else needs to have IPublicLayerOK on the request:
    if (IPublicLayer.providedBy(request) and
        not IPublicLayerOK.providedBy(request)):
        raise NotFound()
