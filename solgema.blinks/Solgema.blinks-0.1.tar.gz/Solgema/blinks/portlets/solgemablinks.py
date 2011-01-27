import urllib2
import socket
import sys

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Acquisition import aq_base, aq_inner, aq_parent
from zope import schema
from zope.formlib import form

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import utils
from plone.portlet.collection import PloneMessageFactory as _pmf
from Solgema.blinks.config import _

class ISolgemaBlinksPortlet(IPortletDataProvider):
    """A portlet which renders the links given by www.b-links.fr.
    """

    header = schema.TextLine(title=_pmf(u"Portlet header"),
                             description=_pmf(u"Title of the rendered portlet"),
                             required=False)

    key = schema.TextLine(title=_(u"label_blinks_key"),
                             description=_(u"description_blinks_key"),
                             required=True)

    urls = schema.Text(title=_(u"label_blinks_urls"),
                             description=_(u"description_blinks_urls"),
                             required=True)

                       
class Assignment(base.Assignment):

    implements(ISolgemaBlinksPortlet)

    header = u""
    key = u""
    urls = u""

    def __init__(self, header=u"", key=u"", urls=u""):
        self.header = header
        self.key = key
        self.urls = urls

    @property
    def title(self):
        return self.header
        
class Renderer(base.Renderer):

    render = ViewPageTemplateFile('solgemablinks.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.blinks = self.isCurrentUrl() and self.getBLinks() or ''

    def getUrls(self):
        return [str(a.replace('http://','')) for a in self.data.urls.split('\n')]

    def isCurrentUrl(self):
        parent = aq_inner(self.context)
        while utils.isDefaultPage(parent, self.request):
            parent = aq_parent(parent)
        if parent.absolute_url().replace('http://','') in self.getUrls():
            return True
        return False

    @property
    def available(self):
        return len(self.blinks)

    def getBLinks(self):
        host = 'http://www.b-links.fr'
        key = self.data.key
        parent = aq_inner(self.context)
        while utils.isDefaultPage(parent, self.request):
            parent = aq_parent(parent)

        here_url = parent.absolute_url().replace('http://','')
        timeout = 2
        socket.setdefaulttimeout(timeout)

        the_url = host+key+here_url
        req = urllib2.Request(the_url)
        try:
            handle = urllib2.urlopen(req)
        except:
            return ''
        the_page = handle.read()
        if the_page:
            the_page = '<ul>'+''.join(['<li>'+link+'</a></li>' for link in the_page.split('</a>') if link])+'</ul>'
        return the_page

class AddForm(base.AddForm):

    form_fields = form.Fields(ISolgemaBlinksPortlet)
    
    label = _(u"label_add_solgemablinks_portlet")
    description = _(u"This portlet display a listing of links given by www.b-links.fr. Please check www.b-links.fr to get all the infos.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):

    form_fields = form.Fields(ISolgemaBlinksPortlet)
    label = _(u"label_edit_solgemablinks_portlet")
    description = _(u"description_solgemablinks_portlet")
