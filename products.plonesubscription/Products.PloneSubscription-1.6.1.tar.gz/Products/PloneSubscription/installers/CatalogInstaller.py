# -*- coding: utf-8 -*-
## ProductName
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
 *******************************************************************
 ** (Un)installation of indexes and meta data in the catalog tool **
 *******************************************************************

 Example:

    ...
    newIndexes = (
        ('stuff', 'FieldIndex', None),
        ('foo', 'DateIndex', None),
        ('bar', 'KeywordIndex', None),
        ('rub', 'ZCTextIndex', {'lexicon_id': 'plone_lexicon',
                                'index_type': 'Okapi BM25 Rank',},),
        )
    ci = CatalogInstaller(newIndexes, metadata=('stuff', 'bar'))
    ...

"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: CatalogInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


from utils import InstallerBase

__all__ = ('CatalogInstaller',)


class args:
    """class for index creation extra arguments"""
    def __init__(self, **kw):
        self.__dict__.update(kw)


class CatalogInstaller(InstallerBase):

    _installerTitle = "indexes and metadata in portal catalog"


    def __init__(self, indexes, metadata=(), **kw):
        """Constructor
        @param indexes: sequence of (id, type, extra) that define new indexes.
        @param metadata: (sequence of) metadata to be added
        @param kw: override defaults like stop_on_error attribute
        """
        self.indexes = indexes
        if type(metadata) == type(''):
            metadata = [metadata]
        self.metadata = tuple(metadata)
        for k, v in kw.items():
            setattr(self, k, v)
        return


    def doInstall(self, context):
        """Adds the indexes and metadata
        @param context: InstallationContext object
        """
        from Products.PloneSubscription.config import Log, LOG_DEBUG
        installed_indexes = context.portal_catalog.indexes()
        for name, type, extra in self.indexes:
            Log(LOG_DEBUG, name, type)
            Log(LOG_DEBUG, name not in installed_indexes, installed_indexes)
            if name not in installed_indexes:
                if extra:
                    context.portal_catalog.addIndex(name, type, extra=args(**extra))
                else:
                    context.portal_catalog.addIndex(name, type)
                context.logInfo("Index '%s' added to portal catalog" % name)
                context.portal_catalog.reindexIndex(name, None)
            else:
                context.logWarning("Index '%s' already exists, skipped" % name)
        installed_indexes = context.portal_catalog.indexes()
        installed_metadata = context.portal_catalog.schema()
        for name in self.metadata:
            if name not in installed_metadata:
                context.portal_catalog.addColumn(name)
                context.logInfo("Metadata '%s' added to portal catalog" % name)
            else:
                context.logWarning("Metadata '%s' already exists, skipped" % name)
        return


    def doUninstall(self, context):
        """Removes indexes and metadata
        @param context: InstallationContext object
        """
        installed_indexes = context.portal_catalog.indexes()
        for name, type, extra in self.indexes:
            if name in installed_indexes:
                context.portal_catalog.delIndex(name)
                context.logInfo("Index '%s' removed from portal catalog" % name)
            else:
                context.logWarning("Index '%s' doesn't exist, removal skipped" % name)
        installed_metadata = context.portal_catalog.schema()
        for name in self.metadata:
            if name in installed_metadata:
                context.portal_catalog.delColumn(name)
                context.logInfo("Metadata '%s' removed from portal catalog" % name)
            else:
                context.logWarning("Metadata '%s' doesn't exist, skipped" % name)
        return
