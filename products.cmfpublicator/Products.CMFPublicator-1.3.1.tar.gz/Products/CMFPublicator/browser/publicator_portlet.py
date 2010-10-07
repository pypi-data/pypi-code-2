# -*- coding: utf-8 -*-

from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from Products.CMFPublicator import MessageFactory as _


class IPublicatorPortlet(IPortletDataProvider):
    """
    """

    box_id = schema.ASCIILine(title=_(u'Box Id'),
                              description=_(u'The id of the publicator box.'),
                              required=True,
                              default="news")

    box_title = schema.TextLine(title=_(u'Portlet Title'),
                                description=_(u'The title of the publicator portlet.'),
                                required=False,
                                default=_(u"News"))

class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(IPublicatorPortlet)

    def __init__(self, box_id="",box_title=""):
        self.box_id = box_id
        self.box_title = box_title

    @property
    def title(self):
        return _(u"Publicator Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.
    """
    
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.box_id = data.box_id
    
    @property
    def available(self):
        return True
    
    _template = ViewPageTemplateFile('publicator_portlet.pt')

    def render(self):
        return xhtml_compress(self._template())

    def publicator_items(self):
        return self._data()

    def box_title(self):
        return self.data.box_title
    
    def check_permission(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        return mtool.checkPermission('Review portal content', context)

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        publicator = getToolByName(context, 'portal_publicator')
        box_id = self.data.box_id
        pb = publicator.getPublicationBoxesInfo(box_id)
        return pb['items']

class AddForm(base.AddForm):
    form_fields = form.Fields(IPublicatorPortlet)
    label = _(u"Add Publicator Portlet")
    description = _(u"This portlet displays items from publicator.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IPublicatorPortlet)
    label = _(u"Edit Publicator Portlet")
    description = _(u"This portlet displays items from publicator.")