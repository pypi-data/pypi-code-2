# -*- coding: utf-8 -*-

from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from DateTime import DateTime
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

class IKmlControlsPortlet(IPortletDataProvider):
    """Interfaccia per la portlet KML"""

class Assignment(base.Assignment):
    implements(IKmlControlsPortlet)

    @property
    def title(self):
        return u"Controlli della mappa"

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('kml_controls.pt')

    @property
    def available(self):
        return bool(self.kmls)

    @property
    @memoize
    def kmls(self):
        """La lista di tutti i KML del contenuto"""
        try:
            kmls = self.context.getRelatedItems()
            kmls = [x.Title() for x in kmls if hasattr(x, 'getFilename') and x.getFilename().endswith(".kml")]
        except AttributeError:
            kmls = []
        return kmls

class AddForm(base.NullAddForm):
    label = u"Aggiungi controlli KML"
    description = "Aggiunge la portlet per i controlli delle mape di Google che mostrano informazioni KML."

    def create(self):
        assignment = Assignment()
        return assignment
