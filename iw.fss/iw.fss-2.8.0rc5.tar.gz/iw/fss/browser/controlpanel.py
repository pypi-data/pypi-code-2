## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

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

# $Id: controlpanel.py 93246 2009-07-28 16:49:10Z glenfant $
"""
Control panel views
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

#Python imports
import os
import urlparse

# Zope imports
from zope.app.component.hooks import getSite
from zope.component import getUtility
from reStructuredText import HTML
from AccessControl.requestmethod import postonly

# Other components imports
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

# Product imports
from iw.fss.config import ZCONFIG, CONFIG_FILE
from iw.fss.utils import FSSMessageFactory as _
from iw.fss.interfaces import IConf
from iw.fss.zcml import patchedTypesRegistry
from iw.fss.migration import Migrator


class FSSBaseView(BrowserView):

    def __init__(self, context, request):
        super(FSSBaseView, self).__init__(context, request)
        conf_class = getUtility(IConf, "globalconf")
        self.conf = conf_class()
        return


    def configletTabs(self):
        """Data for drawing tabs in FSS config panel"""

        this_view = urlparse.urlsplit(self.request.URL)[2].split('/')[-1]

        tab_infos = [
            {'label': _(u'management_tab', default=u"Management"),
             'template': 'fss_management_form'},
            {'label': _(u'maintenance_tab', default=u"Maintenance"),
             'template': 'fss_maintenance_form'},
            {'label': _(u'migration_tab', default=u"Migration"),
             'template': 'fss_migration_form'},
            {'label': _(u'documentation_tab', default=u"Documentation"),
              'template': 'fss_documentation_form'}
            ]

        for ti in tab_infos:
            if ti['template'] == this_view:
                ti['css_class'] = 'selected'
            else:
                ti['css_class'] = None
        return tab_infos


    def rdfEnabled(self):
        return self.conf.rdfEnabled


    def usesGlobalConfig(self):
        """If this site uses the global configuration"""

        return self.conf.usesGlobalConfig()


    def patchedTypesInfo(self):
        """A TALES friendly summary of content types with storage changed to FSS"""

        out = []
        count = -1
        for type_class, fields_to_storages in patchedTypesRegistry.items():
            count += 1
            feature = {'klass': str(type_class)}
            feature['fields'] = [{'fieldname': fn, 'storage': str(st.__class__)}
                                 for fn, st in fields_to_storages.items()]
            feature['row_css_class'] = ('even', 'odd')[count % 2]
            out.append(feature)
        return out



class FSSManagementView(FSSBaseView):
    """The default management view:
    - plone-filesstemstorage.conf settings
    - TTW options
    """


    def globalConfigInfo(self):
        """A TALES friendly configuration info mapping for global configuration"""

        return {
            'config_file': CONFIG_FILE,
            'strategy': ZCONFIG.storageStrategyForSite('/'),
            'storage_path': ZCONFIG.storagePathForSite('/'),
            'backup_path': ZCONFIG.backupPathForSite('/')
            }


    def siteConfigInfo(self):
        """A TALES friendly configuration info mapping for this Plone site"""

        portal = getSite()
        portal_path = '/'.join(portal.getPhysicalPath())
        return {
            'config_file': CONFIG_FILE,
            'strategy': ZCONFIG.storageStrategyForSite(portal_path),
            'storage_path': ZCONFIG.storagePathForSite(portal_path),
            'backup_path': ZCONFIG.backupPathForSite(portal_path)
            }


    def rdfScript(self):
        """Name of ..."""

        return self.conf.rdfScript


    @postonly
    def changeOptions(self, REQUEST):
        """Form handler"""

        rdf_enabled = bool(REQUEST.get('rdf_enabled', None))
        rdf_script = REQUEST.get('rdf_script', '').strip()
        self.conf.rdfEnabled = rdf_enabled
        self.conf.rdfScript = rdf_script
        message = _(
            u'message_properties_saved',
            default=u"Properties saved")
        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
        REQUEST.RESPONSE.redirect(REQUEST.URL1)
        return



class FSSMaintenanceView(FSSBaseView):

    def getFSSStats(self):
        """
        Returns stats on FileSystem storage
        valid_files_count -> Count of valid files
        not_valid_files_count -> Count of not valid files
        valid_backups_count -> Count of valid backups
        not_valid_backups_count -> Count of not valid backups
        """

        storage_brains = self.conf.getStorageBrains()
        backup_brains = self.conf.getBackupBrains()

        valid_files = [x for x in storage_brains if x['path'] is not None]
        not_valid_files = [x for x in storage_brains if x['path'] is None]
        valid_backups = [x for x in backup_brains if x['path'] is None]
        not_valid_backups = [x for x in backup_brains if x['path'] is not None]


        # Sort valid files by size
        def cmp_size(a, b):
              return cmp(a['size'], b['size'])

        valid_files.sort(cmp_size)

        # Size in octets
        total_size = 0
        largest_size = 0
        smallest_size = 0
        average_size = 0

        for x in valid_files:
            total_size += x['size']

        if len(valid_files) > 0:
            largest_size = valid_files[-1]['size']
            smallest_size = valid_files[0]['size']
            average_size = int(total_size / len(valid_files))

        return {
            'valid_files_count' : len(valid_files),
            'not_valid_files_count' : len(not_valid_files),
            'valid_backups_count' : len(valid_backups),
            'not_valid_backups_count' : len(not_valid_backups),
            'total_size' : total_size,
            'largest_size': largest_size,
            'smallest_size' : smallest_size,
            'average_size' : average_size,
            }


    @postonly
    def updateFSS(self, REQUEST):
        """Removed all invalid files"""
        not_valid_files, not_valid_backups = self.conf.updateFSS()
        results = {
            u'not_valid_files': not_valid_files,
            u'not_valid_backups': not_valid_backups}
        message = _(
            u'report_fss_updated',
            default=u"${not_valid_files} files for invalid content moved to backup. ${not_valid_backups} files for invalid backups moved to storage.",
            mapping=results)
        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
        REQUEST.RESPONSE.redirect(REQUEST.URL1)
        return

    @postonly
    def removeBackups(self, REQUEST):
        """Remove backup older than x day"""
        max_days = REQUEST.get("max_days", None)
        if max_days is None:
            max_days = 0
        self.conf.removeBackups(max_days)
        message = _(u'report_old_backups_removed', default=u"Old backups have been removed.")
        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
        REQUEST.RESPONSE.redirect(REQUEST.URL1)
        return

    @postonly
    def updateRDF(self, REQUEST):

        self.conf.updateRDF()
        message = _(u'report_rdf_updated', default=u"RDF files have been updated.")
        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
        REQUEST.RESPONSE.redirect(REQUEST.URL1)
        return


class FSSMigrationView(FSSBaseView):

    def mayMigrate(self):
        """Have enough conditions to let the admin migrate"""

        return (not self.usesGlobalConfig()) and (len(self.patchedTypesInfo()) > 0)


    @postonly
    def migrateToFSS(self, REQUEST):
        """Let's migrate all relevant site content fields"""

        really_migrate = REQUEST.get('imsure', None)
        if not really_migrate:
            message = _(
                u'report_no_migration',
                default=u"You didn't check \"I'm sure\", migration canceled")
            IStatusMessage(REQUEST).addStatusMessage(message, type='info')
            REQUEST.RESPONSE.redirect(REQUEST.URL1)
            return

        # We do it really...
        do_log = bool(REQUEST.get('logtomigration', False))
        commit_every = REQUEST.get('transactioncount')
        migrator = Migrator(getSite(), do_log, commit_every)
        count = migrator.migrateToFSS()
        results = {
            u'count': count}
        message = _(
            u'report_migration_to_fss',
            default=u"${count} content items migrated to FSS",
            mapping=results)
        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
        REQUEST.RESPONSE.redirect(REQUEST.URL1)
        return


    @postonly
    def migrateFromFSS(self, REQUEST):
        """Let's return to original storage"""
        return


class FSSDocumentationView(FSSBaseView):
    """Shows iw.fss documentation"""

    def readMeHtml(self):
        """Renders README.txt (in rst) inside the page"""

        opd = os.path.dirname
        readme_path = os.path.join(os.path.abspath(opd(opd(__file__))), 'README.txt')
        readme_html = HTML(file(readme_path).read(), report_level=100) # No errors/warnings -> faster
        # Fucking header changes the base href, so we need to tweak all href="#..."
        actual_url = self.request.URL
        return readme_html.replace('href="#', 'href="%s#' % actual_url)
