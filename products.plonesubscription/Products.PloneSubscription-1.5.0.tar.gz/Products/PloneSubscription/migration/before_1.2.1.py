# -*- coding: utf-8 -*-
## PloneSubscription
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
Migration script
"""
__version__ = "$Revision: 21241 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: before_1.2.1.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from Products.CMFCore.utils import getToolByName
stool = getToolByName(context, 'portal_subscription')
utool = getToolByName(context, 'portal_url')
portal = utool.getPortalObject()

brains = context.searchResults()
results = []
for brain in brains:
    subscription = brain.getObject()
    kwargs = {}
    folder = subscription.getFolder()
    if folder is None:
        # Plone root site have no UID...
        kwargs['folder'] = stool.UID()
        kwargs['title'] = portal.title_or_id()
        kwargs['workflow'] = False
    else:
        kwargs['title'] = folder.Title()
        kwargs['workflow'] = False

    subscription.edit(**kwargs)
    results.append(subscription.getRpath())

return '\n'.join(results)
