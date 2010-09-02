### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.language.negotiator.interfaces import INegotiatorManager
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from zope.app.security.interfaces import IAuthentication
from zope.component.interfaces import IComponentRegistry
from zope.i18n.interfaces import INegotiator
from zope.location.interfaces import ISite

# import local interfaces
from interfaces import IPathElements, IBaseContent
from interfaces.category import ICategorizedContent
from ztfy.security.interfaces import ISecurityManager
from ztfy.utils.interfaces import INewSiteManagerEvent
from ztfy.utils.timezone.interfaces import IServerTimezone

# import Zope3 packages
from z3c.language.negotiator.app import Negotiator
from zc.catalog.catalogindex import SetIndex, ValueIndex
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.authentication.groupfolder import GroupFolder, GroupInformation
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.catalog.catalog import Catalog
from zope.app.component import hooks
from zope.app.intid import IntIds
from zope.app.generations.utility import findObjectsProviding
from zope.app.publication.zopepublication import ZopePublication
from zope.component import adapter
from zope.location import locate

# import local packages
from ztfy.utils.catalog.index import TextIndexNG
from ztfy.utils.timezone.utility import ServerTimezoneUtility


def updateDatabaseIfNeeded(context, create_catalog=False):
    """Check for missing utilities at application startup"""
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
    if create_catalog:
        # Check authentication utility
        auth = default.get('Authentication')
        if auth is None:
            auth = default['Authentication'] = PluggableAuthentication()
            auth['users'] = PrincipalFolder('usr.')
            groups = auth['groups'] = GroupFolder('grp.')
            groups['administrators'] = GroupInformation('Administrators', 'Site administrators')
            groups['contributors'] = GroupInformation('Contributors', 'Site contributors')
            auth.credentialsPlugins = [ u'No Challenge if Authenticated',
                                        u'Session Credentials',
                                        u'Zope Realm Basic-Auth' ]
            auth.authenticatorPlugins = [ u'users', u'groups' ]
            IComponentRegistry(sm).registerUtility(auth, IAuthentication)
            ISecurityManager(context).grantRole('ztfy.BlogManager', 'grp.administrators', False)
            ISecurityManager(context).grantRole('ztfy.BlogContributor', 'grp.contributors', False)
        # Check server timezone
        tz = default.get('Timezone')
        if tz is None:
            tz = default['Timezone'] = ServerTimezoneUtility()
            IComponentRegistry(sm).registerUtility(tz, IServerTimezone)
        # Check I18n negotiator
        i18n = default.get('I18n')
        if i18n is None:
            i18n = default['I18n'] = Negotiator()
            i18n.serverLanguage = u'en'
            i18n.offeredLanguages = [u'en']
            IComponentRegistry(sm).registerUtility(i18n, INegotiator)
            IComponentRegistry(sm).registerUtility(i18n, INegotiatorManager)
    # Check for required catalog and index
    catalog = default.get('Catalog')
    if (catalog is None) and create_catalog:
        catalog = default['Catalog'] = Catalog()
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'Catalog')
    if catalog is not None:
        if 'paths' not in catalog:
            catalog['paths'] = SetIndex('paths', IPathElements, False)
        if 'categories' not in catalog:
            catalog['categories'] = SetIndex('categories_ids', ICategorizedContent, False)
        if 'content_type' not in catalog:
            catalog['content_type'] = ValueIndex('content_type', IBaseContent, False)
        if 'title' not in catalog:
            catalog['title'] = TextIndexNG('title shortname description heading', IBaseContent, False,
                                           languages=('fr en'),
                                           storage='txng.storages.term_frequencies',
                                           dedicated_storage=False,
                                           use_stopwords=True,
                                           use_normalizer=True,
                                           ranking=True)


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
