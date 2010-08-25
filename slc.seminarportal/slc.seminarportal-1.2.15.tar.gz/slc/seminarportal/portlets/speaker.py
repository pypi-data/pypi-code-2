import logging
import random

from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from interfaces import ISpeakerPortlet

log = logging.getLogger('slc.seminarportal/portlets/speaker.py')


class AddForm(base.AddForm):
    form_fields = form.Fields(ISpeakerPortlet)
    label = _(u"Add a Speaker Portlet")

    def create(self, data):
        return Assignment(featured_speakers=data.get('featured_speakers'),
                          count=data.get('count'),
                          random=data.get('random'),
                          )


class EditForm(base.EditForm):
    form_fields = form.Fields(ISpeakerPortlet)
    label = _(u"Edit the Speaker Portlet")


class Assignment(base.Assignment):
    implements(ISpeakerPortlet)

    def __init__(self, featured_speakers=None, count=5, random=True):
        self.featured_speakers = featured_speakers
        self.count = count
        self.random = random 

    @property
    def title(self):
        return _(u"Featured Speakers")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('speaker.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), 
                                       name=u'plone_portal_state'
                                       )
        self.portal = portal_state.portal()

    def _render_cachekey(method, self):
        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()
        path = "/".join(self.context.getPhysicalPath())
        return (preflang, path)
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.get_speakers() and True or False
        
    def get_speakers(self):
        """ Return the speaker objects as configured by the portlet.
        """
        data = self.data
        if data.random:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains =  catalog(portal_type='SPSpeaker')
            random_indexes = random.sample(range(0, len(brains)),
               (len(brains) >= data.count and data.count or len(brains))) 
            return [brains[i].getObject() for i in random_indexes]

        elif len(data.featured_speakers) > data.count:
            featured_speakers = []
            for i in random.sample(range(0, len(data.featured_speakers), data.count)):
                try:
                    featured_speakers.append(self.portal.unrestrictedTraverse(data.speaker[i]))
                except AttributeError:
                    log.warn('Could not find speaker: %s' % data.speaker[i])
                    self.data.featured_speakers.remove(data.speaker[i])

        elif data.featured_speakers:
            featured_speakers = []
            for speaker in data.featured_speakers:
                try:
                    featured_speakers.append(self.portal.unrestrictedTraverse(speaker))
                except AttributeError:
                    log.warn('Could not find speaker: %s' % speaker)
                    self.data.featured_speakers.remove(speaker)
            return featured_speakers

        return []



