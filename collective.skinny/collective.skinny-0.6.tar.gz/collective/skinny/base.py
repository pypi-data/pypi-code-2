import sys
import warnings

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class RenderError(Exception):
    pass

def render_viewlet(factory, view):
    context = aq_inner(view.context)
    viewlet = factory(context, view.request, None, None).__of__(context)
    viewlet.update()
    return viewlet.render()

class BaseView(BrowserView):
    """Base class to hold useful methods for all our views.
    """
    template_path = 'templates/'
    parts = {}

    def render_template(self, name):
        self = self.__of__(aq_inner(self.context))
        self.rendered_template = ViewPageTemplateFile(
            '%s%s.pt' % (self.template_path, name))
        return self.rendered_template(self)

    def render_part(self, name):
        view = self.parts[name](aq_inner(self.context), self.request)
        return view.__of__(aq_inner(self.context))()

    def __getattr__(self, name):
        if name.startswith('render_'):
            try:
                part_name = name.split('render_')[1]
                if part_name in self.parts:
                    return self.render_part(part_name)
                else:
                    return self.render_template(part_name)
            except AttributeError, e:
                # Because AttributeErrors will otherwise be buried
                # thanks to the ``__getattr__`` contract, we'll try to
                # provide a more useful error behaviour here, see
                # http://blog.ianbicking.org/2007/09/12/re-raising-exceptions
                exc_class, exc, tb = sys.exc_info()
                new_exc = RenderError(
                    "AttributeError: %s while trying to render %r" %
                    (exc, part_name))
                raise RenderError, new_exc, tb
        elif name.startswith('portal_'):
            tool_name = name.split('portal_')[1]
            tools = aq_inner(self.context).restrictedTraverse('@@plone_tools')
            return getattr(tools, tool_name)()
            
        raise AttributeError(name)

    def get_part(self, name):
        warnings.warn('get_part() deprecated; use render_%s()' % name,
                      DeprecationWarning, 2)
        return getattr(self, 'render_%s' % name)
