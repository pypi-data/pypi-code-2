from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base

from interfaces import ISpeechesPortlet

class AddForm(base.AddForm):
    form_fields = form.Fields(ISpeechesPortlet)
    
    label = _(u"Add a Speeches Portlet")

    def create(self, data):
        return Assignment(count=data.get('count'),)


class EditForm(base.EditForm):
    form_fields = form.Fields(ISpeechesPortlet)
    label = _(u"Edit the Speeches Portlet")


class Assignment(base.Assignment):
    implements(ISpeechesPortlet)

    def __init__(self, count=None):
        self.count = count

    @property
    def title(self):
        return _(u"Featured Speeches")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('speeches.pt')

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

    def results(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            count = self.data.count
        except AttributeError:
            count = 5
        if count > 0:
            return catalog(portal_type='SPSpeech', 
                        sort_limit=count, 
                        sort_on='modified', 
                        sort_order='reverse')[:count]
        else:
            return []


