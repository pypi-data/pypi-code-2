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
PloneSubscription package
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: __init__.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Python imports
import sys
from Globals import package_home

# CMF imports
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory

# Archetypes imports
from Products.Archetypes.public import process_types, listTypes

# Products imports
from Products.PloneSubscription.config import SKINS_DIR, GLOBALS, PROJECTNAME, TOOL_ICON
from Products.PloneSubscription import SubscriptionPermissions

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    # Import types
    # Import tool
    from Products.PloneSubscription.content import *
    from Products.PloneSubscription.SubscriptionTool import SubscriptionTool
    from Products.PloneSubscription import SubscriptionPermissions
    from Products.PloneSubscription.config import *

    listOfTypes = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(listOfTypes, PROJECTNAME)

    # A brief explanation for the following code:
    #
    # We want to have another add permission for the topic and
    # criteria because topics shouldn't be addable by non
    # managers. The following code iterats over all content types and
    # seperates the content_types using the interfaces. At last it
    # initializes topic/criteria and the rest with two different
    # permissions.

    subscribers_content_types = []
    subscribers_constructors  = []
    subscriptions_content_types = []
    subscriptions_constructors  = []
    other_content_types = []
    other_constructors  = []

    for i in range(len(listOfTypes)):
        ptai = content_types[i]
        if ptai.portal_type in ('AnonymousSubscriber', 'UserSubscriber',):
            subscribers_content_types.append(content_types[i])
            subscribers_constructors.append(constructors[i])
        elif ptai.portal_type in ('KeywordsSubscription',
                                  'FolderSubscription',
                                  'ContentSubscription',
                                  'ExactSearchSubscription'):
            subscriptions_content_types.append(content_types[i])
            subscriptions_constructors.append(constructors[i])
        else:
            other_content_types.append(content_types[i])
            other_constructors.append(constructors[i])

    # other
    ContentInit(
        PROJECTNAME + ' Content',
        content_types = tuple(other_content_types),
        permission = SubscriptionPermissions.ManageSubscriptionContent,
        extra_constructors = tuple(other_constructors),
        fti = ftis,
        ).initialize(context)

    # Subscription provider
    ContentInit(
        PROJECTNAME + ' Subscriber',
        content_types = tuple(subscribers_content_types),
        permission = SubscriptionPermissions.AddSubscriptionContent,
        extra_constructors = tuple(subscribers_constructors),
        fti = ftis,
        ).initialize(context)

    # Subscription provider
    ContentInit(
        PROJECTNAME + ' Subscription',
        content_types = tuple(subscriptions_content_types),
        permission = SubscriptionPermissions.ViewSubscriptionContent,
        extra_constructors = tuple(subscriptions_constructors),
        fti = ftis,
        ).initialize(context)


    ToolInit(
        '%s Tool' % PROJECTNAME,
        tools=(SubscriptionTool,),
        icon=TOOL_ICON).initialize(context)
