# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

from zope import schema
from zope.formlib import form
from z3c.form.browser.multi import MultiWidget

from Products.CMFPlone import PloneMessageFactory as _
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from logging import getLogger
from DateTime import DateTime
#from metnav.browser import getRscIcon

#logger = getLogger("News View")

class IRecent2Portlet(IPortletDataProvider):
    """
    A portlet displaying a the recent2

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(title=_(u"Titre du portlet nouveautés"),
                            description=_(u"Saisissez le titre du portlet nouveautés."),
                            default= _(u"Nouveautés du site"),
                            required=True)
    count = schema.Int(title=_(u"Nombre d'éléments à afficher"),
                            description=_(u"Saisissez le nombre d'éléments affichés."),
                            required=True,
                            default=5)


class Assignment(base.Assignment):

    implements(IRecent2Portlet)

    def __init__(self, portlet_title=_(u"Les nouveautés du site"), count=5):
        self.count = count
        self.portlet_title = portlet_title
        
    def title(self):
        return self.data.portlet_title
class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/recent2.pt')

    def update(self):
        pp_tool = getToolByName(self.context, 'portal_properties')
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.metadataNav = getToolByName(self.context, 'portal_metadataNav')
        self.meta_url = pp_tool.metnav_properties.getProperty('COLLECTION_METADATA')

    def render(self):
        return self._template()
    
    @property
    def title(self):
        return self.data.portlet_tittle
    
    def recentTitle(self):
        return self.data.portlet_title
    
    def recentNbr(self):
        return self.data.count
    
   
    def searchRecentXMLDocs(self, types=[], dateMax="1901-01-01", fullpath=False):

        context = self.context
        exist = context.exist
        nbrNvt = self.data.count
        meta_url = self.meta_url
        strType = ""

        if types != []:
            strType = """[lomfrens:ensData/lomfrens:ensDocumentType[1]/lomfrens:value/text() | '%s']""" % ' '.join(types)
        else:
            strType = """[not(lomfrens:ensData/lomfrens:ensDocumentType[1]/lomfrens:value/text() = 'question')]"""
     
        mn_tool = getToolByName(self.context, 'portal_metadataNav')
        
        query = self.context.xq_recent2.__str__() % {
            'meta_url':meta_url,
            'date_max': dateMax,
            'site_url': self.site_url,
            }

        da = mn_tool.getDA()
        results = da.query(query)

        liste = []
        for res in results.getDict():
            dico = { 'id'     : res['res/id'][0],
                     'Title'  : res['res/title'][0],
                     'getURL' : res['res/url'][0],
                     'Description' : res.get('res/description', [''])[0],
                     'Date'   : res['res/date'][0],
                     'getIcon':context.getRscIcon(res.get('res/type', [''])[0]),
                     'Type'   : res.get('res/type', [''])[0],

                    }
            #'Creator': res.get('res/creator', [''])[0],
            #if dico['Date'] > dico['ModificationDate'] :
                #dico['ModificationDate'] = dico['Date']
            #dico['getIcon'] = container.getRscIcon(res.get('res/mime', [''])[0], res.get('res/type', [''])[0])
                  
            #"""if res['res/mime'][0] == 'text/xml':
            #if fullpath:
            #    dico['getURL'] = path + "?url=" + dico['getURL']
            #else:
                #dico['getURL'] = path + "?url=" + dico['getURL']"""
            liste.append(dico)
            
        return liste
        #return str(res)
     
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRecent2Portlet)
    label=_(u"Ajouter le portlet Nouveautés du site")
    description=_(u"Ce portlet affiche les nouveautés du site.")

    def create(self, data):
        return Assignment()

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRecent2Portlet)
    label=_(u"Editer le portlet Nouveautés du site")
    description=_(u"Ce portlet affiche les nouveautés du site.")