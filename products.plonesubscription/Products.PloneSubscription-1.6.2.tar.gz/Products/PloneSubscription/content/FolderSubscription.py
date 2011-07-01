# -*- coding: utf-8 -*-
## PloneSubscription
## A Plone tool supporting different levels of subscription and notification
## Copyright (C)2006 Ingeniweb

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
"""
This module implement a folder subscription with recursivity ans workflow options
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: FolderSubscription.py 241711 2011-06-30 15:01:43Z yboussard $
__docformat__ = 'restructuredtext'


# Python imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent

# Zope imports
from DateTime import DateTime

# CMF imports
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import *
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *

# Products imports
from Products.PloneSubscription.config import PROJECTNAME, TOOL_META_TYPE
from Products.PloneSubscription.content.schemata import BaseSubscriptionSchema
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscription import ISubscription

schema = BaseSubscriptionSchema.copy() + Schema ((
    ReferenceField(
        'folder',
        multiValued=False,
        required=True,
        searchable=False,
        relationship='subscriptionFolderOf',
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.EditSubscriptionContent,
        widget=ReferenceBrowserWidget(
            addable=True,
            visible={ 'view': 'hidden', 'edit': 'visible',},
            label="Folder subscribed",
            label_msgid="label_subscription_folder",
            description="The folderish document on which the subscription is done.",
            description_msgid="help_subscription_folder",
            i18n_domain="plonesubscription",
            default_search_index='Title',
            available_indexes={'Title': 'title',}
            ),
        ),
    BooleanField(
        'recursive',
        multiValued=False,
        required=False,
        searchable=False,
        default=True,
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.EditSubscriptionContent,
        widget=BooleanWidget(
            addable=True,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Recursive",
            label_msgid="label_subscription_recursive",
            description="Recursive search.",
            description_msgid="help_subscription_recursive",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'workflow',
        multiValued=False,
        required=False,
        searchable=False,
        default=False,
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.EditSubscriptionContent,
        widget=BooleanWidget(
            addable=True,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Workflow transition",
            label_msgid="label_subscription_workflow",
            description="Only return documents which passed a workflow transition",
            description_msgid="help_subscription_workflow",
            i18n_domain="plonesubscription",
            ),
        ),
    LinesField(
        'transitions',
        multiple = 1,
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.EditSubscriptionContent,
        widget = LinesWidget(
            label_msgid = "label_transitions",
            description_msgid = "help_transitions",
            i18n_domain = "plonesubscription",
            ),
        ),
#    LinesField(
#        'meta_types',
#        multiple = 1,
#        #vocabulary = "getAvailableContentTypesVocabulary",
#        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
#        write_permission=SubscriptionPermissions.EditSubscriptionContent,
#        widget = LinesWidget(
#            label_msgid = "label_meta_types",
#            description_msgid = "help_meta_types",
#            i18n_domain = "plonesubscription",
#            ),
#        ),
    ),)

class FolderSubscription(BaseContent):
    """Implement folder subscription"""

    __implements__ = BaseContent.__implements__, ISubscription

    portal_type = meta_type = 'FolderSubscription'
    archetype_name = 'FolderSubscription'
    immediate_view = 'base_view'
    default_view   = 'base_view'
    content_icon = 'foldersubscription_icon.gif'
    global_allow = False
    schema =  schema
    allowed_content_types = ()
    include_default_actions = 0
    security = ClassSecurityInfo()

    actions = (
        {
        'id'            : 'view',
        'name'          : 'View',
        'action'        : 'string:${object_url}/base_view',
        'permissions'   : (SubscriptionPermissions.ViewSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
        {
        'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'string:${object_url}/base_edit',
        'permissions'   : (SubscriptionPermissions.ViewSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
    )

    # Fields related methods
    def getFolder(self):
       folder = self.getField('folder').get(self)
       if folder is None:
           return None
       else:
           if getattr(folder, 'meta_type', '') == TOOL_META_TYPE:
               return folder.getParentNode()
           else:
               return folder

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getRpath')
    def getRpath(self):
        """Overload rpath accessor to synchronise reference"""
        folder = self.getFolder()
        if folder is None:
            return self.getField('rpath').get(self)
        else:
            return '/'.join(folder.getPhysicalPath())

    security.declareProtected(SubscriptionPermissions.EditSubscriptionContent, 'setRpath')
    def setRpath(self, rpath='/'):
        """Overload rpath mutator for forward compatibility"""
        folder = self.getField('folder').get(self)
        if folder is None:
            self.getField('rpath').set(self, rpath)
        else:
            self.getField('rpath').set(self, '/'.join(folder.getPhysicalPath()))

    # Interface related methods

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getSubscriber')
    def getSubscriber(self):
        """Return the subscriber"""
        return aq_parent(aq_inner(self))

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getQuery')
    def getQuery(self):
        """Return the request used for catalog query"""
        path_arg = None
        # customizing request for limited path search
        if not self.getRecursive():
            path_arg = {
                    'query': self.getRpath(),
                    'depth': 0,
                    }
        else:
            path_arg = self.getRpath()

        query = {
            'path': path_arg,
            'modified': {
                'query': [self.getLast_send(),],
                'range': 'min'
                },
            'language': "",
            }
        ## LP !!!
        obj = self.getFolder()
        if hasattr(obj.aq_base, 'getTranslations'):
            query['path'] = []
            for x in obj.getTranslations().values():
                query['path'].append('/'.join(x[0].getPhysicalPath()))
            
        return query

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getQueryBrains')
    def getQueryBrains(self):
        """Return the list of brains concerned by the mailing"""
        stool = getToolByName(self, 'portal_subscription')
        return stool.getQueryBrains(self.getQuery())

    def afterQueryFilters(self, brains):
        """Filter query results with subscription options"""
        if hasattr(self, 'getWorkflow') and self.getWorkflow():
            stool = getToolByName(self, 'portal_subscription')
            brains= stool.afterQueryWorkflowFilter(brains, self.getLast_send(), transitions=self.transitions)
        return brains

    def getSubscriptionUrl(self):
        """Return the url of the object or concept subscribed on"""
        return self.getRpath()

#    def getAvailableContentTypesVocabulary(self):
#        portal_types = getToolByName(self, 'portal_types')
#        atool = getToolByName(self, 'archetype_tool')
#        # Build dictionnary meta_type -> schema
#        at_meta_types = [x['meta_type'] for x in atool.listRegisteredTypes()]
#        type_infos = portal_types.listTypeInfo()
#        types = []
#        for type_info in type_infos:
#            meta_type = type_info.Metatype()
#            if meta_type in at_meta_types:
#                types.append(type_info.getId())
#        lst = list([[x, x, x] for x in types])
#        lst.insert(0, ['all', 'all', 'option_all', ])
#        return DisplayList(lst)


registerType(FolderSubscription, PROJECTNAME)
