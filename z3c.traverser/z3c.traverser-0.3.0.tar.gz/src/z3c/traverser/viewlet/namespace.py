from zope import component
from zope.publisher.interfaces import NotFound
from zope.security.proxy import removeSecurityProxy
from zope.traversing.namespace import SimpleHandler
from zope.viewlet.interfaces import IViewletManager

class ViewletViewletManagerHandler(SimpleHandler):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        context = removeSecurityProxy(self.context).context
        provider = component.queryMultiAdapter(
            (context, self.request, self.context),
            IViewletManager, name)
        if provider is None:
            raise NotFound(self.context, name, self.request)

        return provider


class ViewletManagerHandler(SimpleHandler):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        context = self.context.__parent__
        provider = component.queryMultiAdapter(
            (context, self.request, self.context),
            IViewletManager, name)
        if provider is None:
            raise NotFound(self.context, name, self.request)
        return provider


class ViewletHandler(SimpleHandler):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        # Try to look up the viewlet
        viewlet = self.context.get(name)
        if viewlet is None:
            raise NotFound(self.context, name, self.request)
        viewlet = removeSecurityProxy(viewlet)
        # hack: somehow in the viewlet metaconfigure it makes the
        # viewlet class a IBrowserPublisher, which assumes that we
        # have a call in browserdefault, so we have to replace this
        # method.
        viewlet.browserDefault = lambda r: (viewlet, ('index.html',))
        return viewlet

