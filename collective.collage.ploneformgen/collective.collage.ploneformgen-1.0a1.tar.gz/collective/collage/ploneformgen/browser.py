from zope import interface
from zope import component

from Products.PloneFormGen.browser.embedded import EmbeddedPFGView

from Products.Collage.browser import helper
from Products.Collage.browser import views
from Products.Collage.viewmanager import mark_request
from Products.Collage.interfaces import IDynamicViewManager

from Acquisition import aq_inner

from ZPublisher.Publish import Retry

class PloneFormGenView(EmbeddedPFGView, views.BaseView):
    title = u"Standard"

    @property
    def prefix(self):
        return "form-%s" % self.context.UID()

    @property
    def action(self):
        return self.helper.getCollageObject().absolute_url()

    @property
    def helper(self):
        return helper.CollageHelper(self.collage_context, self.request)
    
    @property
    def __call__(self):
        return self.index

    def render_embedded_view(self):
        try:
            return EmbeddedPFGView.__call__(self)
        except Retry:
            # a retry-exception is raised in order for the thank-you
            # page to be rendered; we need to intercept this and do
            # our own rendering of this page
            # and take care in case there's a virtual host monster request involved

            path_translated = self.request._orig_env['PATH_TRANSLATED']

            if 'VirtualHostRoot' in path_translated:
                # Eliminate /VirtualHostBase/ and /VirtualHostRoot parts
                nodes = path_translated.replace('/VirtualHostBase/','').replace('/VirtualHostRoot','').split('/')
                # Eliminates the protocol and server parts
                nodes = nodes[2:]
                path_translated = '/'.join(nodes)

            context = self.context.unrestrictedTraverse(path_translated)
            manager = IDynamicViewManager(context)

            layout = manager.getLayout()
            if not layout:
                layout, title = manager.getDefaultLayout()

            ifaces = mark_request(self.context, self.request)
            view = component.getMultiAdapter((context, self.request), name=layout)
            interface.directlyProvides(self.request, ifaces)
            
            return view()
