### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from zope.app.publication.zopepublication import ZopePublication
from zope.component.interfaces import IComponentRegistry
from zope.location.interfaces import ISite

# import local interfaces
from interfaces import IBaseExtFileInfo
from ztfy.utils.interfaces import INewSiteManagerEvent

# import Zope3 packages
from zc.catalog.catalogindex import ValueIndex
from zope.app.catalog.catalog import Catalog
from zope.app.component import hooks
from zope.app.generations.utility import findObjectsProviding
from zope.app.intid import IntIds
from zope.component import adapter
from zope.location import locate

# import local packages
from ztfy.utils.site import locateAndRegister


def updateDatabaseIfNeeded(context, create_catalog=False):
    """Check for missing objects at application startup"""
    try:
        sm = context.getSiteManager()
    except:
        return
    default = sm['default']
    # Check for required IIntIds utility
    intids = default.get('IntIds')
    if intids is None:
        intids = IntIds()
        locate(intids, default)
        IComponentRegistry(sm).registerUtility(intids, IIntIds, '')
        default['IntIds'] = intids
    # Check for required catalog and index
    catalog = default.get('Catalog')
    if (catalog is None) and create_catalog:
        catalog = Catalog()
        locateAndRegister(catalog, default, 'Catalog', intids)
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'Catalog')
    if catalog is not None:
        if 'filename' not in catalog:
            index = ValueIndex('filename', IBaseExtFileInfo, False)
            locateAndRegister(index, catalog, 'filename', intids)


@adapter(IDatabaseOpenedWithRootEvent)
def handleOpenedDatabase(event):
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    updated = False
    for site in findObjectsProviding(root_folder, ISite):
        if site is not root_folder:
            hooks.setSite(site)
            updateDatabaseIfNeeded(site)
            updated = True
    if not updated:
        hooks.setSite(root_folder)
        updateDatabaseIfNeeded(root_folder)


@adapter(INewSiteManagerEvent)
def handleNewSiteManager(event):
    updateDatabaseIfNeeded(event.object, create_catalog=True)
