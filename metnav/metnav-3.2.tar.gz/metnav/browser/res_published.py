# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.

from Globals import DevelopmentMode
from logging import getLogger

from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

logger = getLogger("News View")

class res_published(BrowserView):

    def searchRecentXMLDocs(self, types=[], dateMax="1901-01-01", fullpath=False):
        
        pp_tool = getToolByName(self.context, 'portal_properties')
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.meta_url = pp_tool.metnav_properties.getProperty('COLLECTION_METADATA')
        
        context = self.context
        exist = context.exist
        strType = ""

        if types != []:
            strType = """[lomfrens:ensData/lomfrens:ensDocumentType[1]/lomfrens:value/text() |= '%s']""" % ' '.join(types)
        else:
            strType = """[not(lomfrens:ensData/lomfrens:ensDocumentType[1]/lomfrens:value/text() = 'question')]"""
     
        mn_tool = getToolByName(self.context, 'portal_metadataNav')
        
        query = self.context.xq_recent2.__str__() % {
            'date_max': dateMax,
            'site_url': self.site_url,
            'meta_url': self.meta_url,
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
                     'Type'   : res.get('res/type', [''])[0],
                     'Creator': res.get('res/creator', [''])[0], 
                     'getIcon':context.getRscIcon(res.get('res/type', [''])[0]),
                    }
            #'Creator': res.get('res/creator', [''])[0], 
            #if dico['Date'] > dico['ModificationDate'] :
                #dico['ModificationDate'] = dico['Date']
            #dico['getIcon'] = context.getRscIcon(res.get('res/type', [''])[0])
                  
            #"""if res['res/mime'][0] == 'text/xml':
            #if fullpath:
            #    dico['getURL'] = path + "?url=" + dico['getURL']
            #else:
                #dico['getURL'] = path + "?url=" + dico['getURL']"""
            liste.append(dico)
            
        return liste
