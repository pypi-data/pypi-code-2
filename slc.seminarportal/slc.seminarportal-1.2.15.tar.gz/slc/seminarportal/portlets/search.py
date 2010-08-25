from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Acquisition import aq_inner

from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from interfaces import ISearchPortlet

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

class Assignment(base.Assignment):
    implements(ISearchPortlet)

    @property
    def title(self):
        return _(u"Search for Seminars, Speakers of Speeches")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('search.pt')

    def _render_cachekey(method, self):
        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()
        return (preflang)
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), 
                                       name=u'plone_portal_state'
                                       )
        self.portal = portal_state.portal()

    @memoize
    def here_url(self):
        context = aq_inner(self.context)
        return '/'.join(context.getPhysicalPath())

    @memoize
    def template_id(self):
        return '@@seminar-search'
        
    def results(self):
        return self._data()

