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
This module implement a simple anonymous subscriber.
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: AnonymousSubscriber.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Zope imports
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit

# CMF imports
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import *

# Products imports
from Products.PloneSubscription.config import PROJECTNAME
from Products.PloneSubscription.content.schemata import BaseSubscriberSchema
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscriber import ISubscriber
from Products.Archetypes.ArchetypeTool import listTypes

anonymous_schema = Schema((
    StringField('fullname',
                  required=1,
                  mode='rw',
                  widget=StringWidget(label='',
                                      description='',
                                      label_msgid='label_fullname',
                                      description_msgid='desc_fullname',
                                      ),
                  ),
    StringField('email',
                required=1,
                mode='rw',
                validators=('isEmail',),
                widget=StringWidget(label='E-mail',
                                    description='Enter your e-mail address here.',
                                    label_msgid='label_email',
                                    description_msgid='desc_email',
                                    ),
                ),
    ))

schema = BaseSubscriberSchema.copy() + anonymous_schema

class AnonymousSubscriber(BaseFolder):
    """Implement subscriber folder for anonymous"""

    __implements__ = BaseFolder.__implements__, ISubscriber

    listOfTypes = listTypes()

    portal_type = meta_type = 'AnonymousSubscriber'
    archetype_name = 'AnonymousSubscriber'
    immediate_view = 'subscriber_view'
    default_view   = 'subscriber_view'
    content_icon = 'anonymoussubscriber_icon.gif'
    global_allow = False
    schema =  schema
    filter_content_types = True
    allowed_content_types = ('FolderSubscription',
                             'KeywordsSubscription',
                             'ContentSubscription',
                             'ExactSearchSubscription',)
    # XXX use property with Zope 2.8 and ZODB 3.4 only
    #allowed_content_types = property(getSubscriberAllowedContentTypes())
    include_default_actions = 0
    security = ClassSecurityInfo()

    actions = (
        {
        'id'            : 'view',
        'name'          : 'View',
        'action'        : 'string:${object_url}/subscriber_view',
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

    def getUsers(self, subscription_id):
        """Return the users concerned by the subscriber"""
        anonymous = AnonymousUser(self.getSubscriberInfo())
        return (anonymous,)

    security.declarePublic('getSubscriberInfo')
    def getSubscriberInfo(self):
        """
        Return 'harmless' info of a subscriber. Fullname and email are required
        information.
        """
        subscriberinfo = { 'type' : "Anonymous",
                           'fullname' : self.getFullname(),
                           'email': self.getEmail(),
                         }
        return subscriberinfo

class AnonymousUser( Implicit ):
    """
      Anonymous USer for unit testing purposes.
    """
    def __init__(self, info):
        self.info=info
    
    def getId( self ):
        return 'Anonymous User'

    getUserName = getId

    def has_permission(self, permission, obj):
        return 1

    def allowed( self, object, object_roles=None ):
        return 1

    def getRoles(self):
        return ('Anonymous',)

    def getProperty(self, property):
        return self.info[property]

registerType(AnonymousSubscriber, PROJECTNAME)
