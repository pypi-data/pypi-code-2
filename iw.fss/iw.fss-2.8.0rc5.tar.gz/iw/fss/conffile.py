# -*- coding: utf-8 -*-
## FileSystemStorage
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
The FileSystemStorage tool
$Id: conffile.py 66391 2008-06-09 17:38:35Z glenfant $
"""

__version__ = "$Revision$"
__docformat__ = 'restructuredtext'

# Python imports
import time

# Zope imports
from zope.interface import implements
#getSite return the context-dependent plone site
from zope.app.component.hooks import getSite
# CMF imports
from Products.CMFCore.utils import getToolByName

# Products imports
from iw.fss.utils import rm_file
from iw.fss.FileSystemStorage import FileSystemStorage
from iw.fss.utils import getFieldValue
from iw.fss.config import ZCONFIG
from iw.fss import strategy as fss_strategy
from iw.fss.interfaces import IConf

# {storage-strategy (from config file): strategy class, ...}
_strategy_map = {
    'flat': fss_strategy.FlatStorageStrategy,
    'directory': fss_strategy.DirectoryStorageStrategy,
    'site1': fss_strategy.SiteStorageStrategy,
    'site2': fss_strategy.SiteStorageStrategy2
    }


class ConfFile(object):
    """Tool for FileSystem storage"""

    implements(IConf)


    @property
    def fssPropertySheet(self):

        portal_properties = getToolByName(getSite(), 'portal_properties')
        return portal_properties.filesystemstorage_properties


    def isRDFEnabled(self):
        """Returns true if RDF is automaticaly generated when file added"""

        return bool(self.fssPropertySheet.rdf_enabled)


    def enableRDF(self, enabled):
        """Enable rdf or not"""

        self.fssPropertySheet.rdf_enabled = bool(enabled)

    rdfEnabled = property(isRDFEnabled, enableRDF)


    def getRDFScript(self):
        """Returns rdf script used to generate RDF on files"""

        return self.fssPropertySheet.rdf_script


    def setRDFScript(self, rdf_script):
        """Set rdf script used to generate RDF on files"""

        self.fssPropertySheet.rdf_script = rdf_script.strip()

    rdfScript = property(getRDFScript, setRDFScript)

    def usesGlobalConfig(self):
        """If the global configuration is in use for this site"""

        portal = getSite()
        return ZCONFIG.usesGlobalConfig(portal)

    def getStorageStrategy(self):
        """Returns the storage strategy"""

        global _strategy_map
        portal = getSite()
        portal_path = '/'.join(portal.getPhysicalPath())
        strategy_class = _strategy_map[ZCONFIG.storageStrategyForSite(portal_path)]
        return strategy_class(
            ZCONFIG.storagePathForSite(portal_path),
            ZCONFIG.backupPathForSite(portal_path))


    def getUIDToPathDictionnary(self):
        """Returns a dictionnary

        For one uid (key) give the correct path (value)
        """

        ctool = getToolByName(getSite(), 'uid_catalog')
        brains = ctool(REQUEST={})
        return dict([(x['UID'], x.getPath()) for x in brains])


    def getPathToUIDDictionnary(self):
        """Returns a dictionnary

        For one path (key) give the correct UID (value)
        """

        ctool = getToolByName(getSite(), 'uid_catalog')
        brains = ctool(REQUEST={})
        return dict([(x.getPath(), x['UID']) for x in brains])


    def getFSSBrains(self, items):
        """Returns a dictionnary.

        For one uid, returns a dictionnary containing of fss item stored on
        filesystem:
        - uid: UID of content
        - path: Path of content
        - name: Name of field stored on filesystem
        - size: Size in octets of field value stored on filesystem
        - fs_path: Path on filesystem where the field value is stored
        """

        if not items:
            return []

        # Get the first item of items list and check if item has uid or path key
        if not items[0].has_key('uid'):
            # Use path to uid dictionnary
            path_to_uid = self.getPathToUIDDictionnary()
            for item in items:
                item['uid'] = path_to_uid.get(item['path'], None)
        else:
            # Use uid to path dictionnary
            uid_to_path = self.getUIDToPathDictionnary()
            for item in items:
                item['path'] = uid_to_path.get(item['uid'], None)

        return items


    def getStorageBrains(self):
        """Returns a list of brains in storage path"""

        strategy = self.getStorageStrategy()
        items = strategy.walkOnStorageDirectory()
        return self.getFSSBrains(items)


    def getStorageBrainsByUID(self, uid):
        """ Returns a list containing all brains related to fields stored
        on filesystem of object having the specified uid"""

        return [x for x in self.getStorageBrains() if x['uid'] == uid]


    def getBackupBrains(self):
        """Returns a list of brains in backup path"""

        strategy = self.getStorageStrategy()
        items = strategy.walkOnBackupDirectory()
        return self.getFSSBrains(items)


    def updateFSS(self):
        """
        Update FileSystem storage
        """

        storage_brains = self.getStorageBrains()
        backup_brains = self.getBackupBrains()

        not_valid_files = tuple([x for x in storage_brains if x['path'] is None])
        not_valid_backups = tuple([x for x in backup_brains if x['path'] is not None])
        strategy = self.getStorageStrategy()

        # Move not valid files in backup
        for item in not_valid_files:
            strategy.unsetValueFile(**item)

        # Move not valid backups in file storage
        for item in not_valid_backups:
            strategy.restoreValueFile(**item)
        return len(not_valid_files), len(not_valid_backups)


    def removeBackups(self, max_days):
        """
        Remove backups older than specified days
        """

        backup_brains = self.getBackupBrains()
        valid_backups = [x for x in backup_brains if x['path'] is None]
        current_time = time.time()

        for item in valid_backups:
            one_day = 86400 # One day 86400 seconds
            modified = item['modified']
            seconds = int(current_time) - int(modified.timeTime())
            days = int(seconds/one_day)

            if days >= max_days:
                rm_file(item['fs_path'])


    def updateRDF(self):
        """Add RDF files to fss files"""

        rdf_script = self.getRDFScript()
        storage_brains = self.getStorageBrains()
        strategy = self.getStorageStrategy()

        for item in storage_brains:
            instance_path = item['path']
            if instance_path is None:
                continue

            try:
                instance = self.restrictedTraverse(instance_path)
            except AttributeError:
                # The object doesn't exist anymore, we continue
                continue
            name = item['name']
            field = instance.getField(name)
            if field is None:
                continue
            storage = field.getStorage(instance)
            if not isinstance(storage, FileSystemStorage):
                continue

            # Get FSS info
            info = storage.getFSSInfo(name, instance)
            if info is None:
                continue

            # Call the storage strategy
            rdf_value = info.getRDFValue(name, instance, rdf_script=rdf_script)
            strategy.setRDFFile(rdf_value, uid=item['uid'], name=name)
        return


    def getFSSItem(self, instance, name):
        """Get value of fss item.
        This method is called from fss_get script.

        @param instance: Object containing FSS item
        @param name: Name of FSS item to get
        """

        return getFieldValue(instance, name)
