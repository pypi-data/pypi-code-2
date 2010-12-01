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
Subscription catalog for quick specific search
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: SubscriptionCatalog.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
#from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.CatalogTool import CatalogTool

# CMF imports
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore  import permissions as CMFCorePermissions

# Archetypes imports
from Products.Archetypes.public import *

# Products imports
from Products.PloneSubscription.config import CATALOG_INDEXES, GLOBALS, PROJECTNAME

class SubscriptionCatalog(UniqueObject, CatalogTool):
    """Catalog for PloneSubscription"""

    id = 'subscription_catalog'
    title = "Subscription catalog"

    def _initIndexes(self):
        # Content indexes
        self._catalog.indexes.clear()
        # Cached metadata
        self._catalog.names = ()
        self._catalog.schema.clear()
        for (index_name, index_type, is_metadata, extra) in CATALOG_INDEXES:
            self.addIndex( index_name, index_type, extra )
            if is_metadata:
                self.addColumn(index_name)


InitializeClass(SubscriptionCatalog)

def manage_addSubscriptionCatalog(self, id, title,
                                  REQUEST=None):
    """Add the vocabulary catalog
    """
    id = str(id)
    title = str(title)
    c = SubscriptionCatalog()
    self._setObject(id, c)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST,update_menu=1)
