# -*- coding: utf-8 -*-
## Copyright (C) 2006-2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from AccessControl import ClassSecurityInfo

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from Products.CMFCore import permissions as CCP
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression


class PloneKeyWordExplorerTool(PropertyManager, UniqueObject, SimpleItem, ActionProviderBase):
    """
    Configuration and "engine" of Plone Keyword Explorer
    """
    id = 'plone_keyword_explorer_tool'
    meta_type = 'PloneKeyWordExplorerTool'
    plone_tool = 1
    title = "PloneKeyWord Explorer Tool"

    manage_options = (

        # FIXME: What's this "overview" (there's no such template)
        ({'label' : 'Overview',
          'action' : 'overview'
          },)
        + ActionProviderBase.manage_options
        + PropertyManager.manage_options
        + SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    _actions = (
        ActionInformation(
            id='keywordexplorer',
            title='Keyword Explorer',
            action=Expression(
                text='string: ${portal_url}/searchkeywords_form'
            ),
            condition=Expression(
                text="python: portal." + id + ".isActionDisplayed(object)"
            ),
            permissions=(CCP.View,),
            category='site_actions',
            visible=True,
        ),
    )


    security.declarePublic('get_documents_for_subjects')
    def get_documents_for_subjects(self, subjects, REQUEST=None):
        documents=[]
        portal_catalog = getToolByName(self, "portal_catalog")
        if subjects:
            ptool = getToolByName(self, 'plone_utils')
            selected_types = ptool.getUserFriendlyTypes()
            for o in portal_catalog.searchResults(
                Subject={'query':subjects,'operator':'and'},
                portal_type=selected_types,
                #review_state = 'published',
                sort_on='portal_type',
                sort_order='reverse'):

                url=o.getURL()
                title=''
                if o.Title:
                    title=o.Title
                else:
                    title=o.getId #getId() is indexed as the getId property
                documents.append( {'title':title
                                 , 'url':url
                                 , 'icon':o.getIcon
                                 , 'subject':o.Subject
                                 , 'author':o.Creator
                                 , 'modified':o.ModificationDate
                                 , 'description':o.Description} )
        return documents


    security.declarePublic('get_documents_without_subjects')
    def get_documents_without_subjects(self, REQUEST=None):
        documents=[]
        portal_catalog = getToolByName(self, "portal_catalog")
        ptool = getToolByName(self, 'plone_utils')
        selected_types = ptool.getUserFriendlyTypes()
        for o in portal_catalog.searchResults(
            #review_state = 'published',
            portal_type=selected_types,
            sort_on = 'portal_type',
            sort_order = 'reverse'):

            if o.Subject:
                pass
            elif o.portal_type in ['Image','Folder']:
                pass
            else:
                documents.append(o)
        return documents


    security.declarePublic('get_other_subjects')
    def get_other_subjects(self, documents, subjects):
        other_subjects={}
        if documents:
            for d in documents:
                for s in d['subject']:
                    if s in subjects:
                        pass # Already existing
                    else:
                        if other_subjects.has_key(s):
                            other_subjects[s]=other_subjects[s]+1
                        else:
                            other_subjects[s]=1
        return other_subjects


    security.declarePublic('get_subjects_url')
    def get_subjects_url(self, subjects, include=None, exclude=None):
        i=0
        url=''

        if include:
            include=[include]
        else:
            include=[]

        for subject in subjects+include:
            if subject==exclude:
                pass # Ignore
            else:
                i+=1
                if i==1:
                    url+='?'
                else:
                    url+='&'
                url+="Subject.query:list:record=" + subject

        if url:
            url+='&Subject.operator:record=and'

        return url


    security.declarePublic('get_subjects')
    def get_subjects(self, subjects_record,):
        """ get subjects from querystring """

        if hasattr(subjects_record, 'query'):
            return subjects_record.query
        else:
            return None

    security.declarePublic('isActionDisplayed')
    def isActionDisplayed(self, objekt):
        return True

InitializeClass(PloneKeyWordExplorerTool)
