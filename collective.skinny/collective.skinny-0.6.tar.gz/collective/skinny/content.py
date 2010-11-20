"""This package contains views for the content area of your page.
"""

from Acquisition import aq_inner, aq_base
from zExceptions import NotFound
import BeautifulSoup

from collective.skinny.base import BaseView

class DefaultView(BaseView):
    """A view for the content area that's used when no other view was
    found.
    """
    def __call__(self):
        return ("<strong>Could not find a view for %r.  You can add one "
                "in the content.py file.</strong>" % self.context.portal_type)

class Registry(BaseView):
    """This view implements a very simple look-up mechanism based on
    the portal type and a dict.  Use adaptation instead if you're
    feeling clever.
    """
    template_path = 'templates/content/'

    allow_fallback_to_plone_views = True

    # Our simple registry of {portal_type: BrowserView}.

    # It also works just to put a template with the portal type name
    # into the ``tempates/content`` directory, like:
    # ``templates/content/document.pt``.
    parts = {
        #'Document': PageView,
        }

    def _set_context_to_default_page(self):
        # Try to look up the default page for context first
        default_name = getattr(aq_base(self.context), 'default_page', '')
        if default_name:
            self.__dict__['context'] = getattr(
                aq_inner(self.context), default_name)

    def __call__(self):
        self._set_context_to_default_page()

        # Now look up an appropriate view or template:
        portal_type = self.context.portal_type
        if portal_type in self.parts:
            return self.render_part(portal_type)
        else:
            try:
                return self.render_template(portal_type.lower())
            except ValueError, e:
                if e.args[0] == 'No such file':
                    if self.allow_fallback_to_plone_views:
                        # As a last resort, we'll try to render the
                        # default view from Plone:
                        return self.render_default_plone_view()
                    else:
                        raise NotFound()
                else:
                    raise

    def render_default_plone_view(self):
        context = aq_inner(self.context)
        html = context.restrictedTraverse(context.getLayout())()

        soup = BeautifulSoup.BeautifulSoup(html)
        content = soup.find('div', attrs={'id': 'content'})
        if content is None:
            content = soup.find('div', attrs=dict({'id': 'region-content'}))

        return content.renderContents(encoding=None) # meaning: as unicode
