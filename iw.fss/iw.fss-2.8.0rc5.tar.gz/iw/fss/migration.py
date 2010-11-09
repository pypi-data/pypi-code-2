## -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb

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

# $Id: migration.py 114464 2010-04-01 16:25:17Z yboussard $
"""
Migration (not upgrades) related resources.
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import logging

import transaction
from OFS.Image import File
from Products.Archetypes.BaseUnit import BaseUnit

from iw.fss import config
from iw.fss.zcml import patchedTypesRegistry

logger = logging.getLogger(config.PROJECTNAME)
LOG = logger.info
LOG_WARNING = logger.warning
LOG_ERROR = logger.error

UNKNOWN_MIMETYPE = 'application/octet-stream'

class Migrator(object):

    def __init__(self, portal, do_log=False, commit_every=0):
        """Construction params:
        @param portal: portal object to migrate
        @param do_log: log details of migration (bool)
        @param commit_every: commit subtransaction every n content items changed
        """
        self.portal = portal
        self.do_log = do_log
        self.commit_every = commit_every
        self.changed_items = 0
        return

    def commit(self):
        """Should we commit?
        """
        self.changed_items += 1
        if ((self.commit_every > 0)
            and (self.changed_items % self.commit_every == 0)):
            transaction.savepoint(optimistic=True)
            self.log("%s items migrated. Commiting...", self.changed_items)
        return

    def log(self, message, *args, **kw):
        """Logging if option set
        Params: see logging module, info method
        http://python.org/doc/2.4.4/lib/node341.html
        """
        if self.do_log:
            LOG(message, *args, **kw)

    def migrateToFSS(self):
        """Do migrations to FSS
        """
        catalog = self.portal.portal_catalog
        mimetypes_registry = self.portal.mimetypes_registry
        self.log("Starting migration to FSS")

        # Looping on relevant content types / fields
        for content_class, patched_fields in patchedTypesRegistry.items():
            meta_type = content_class.meta_type
            self.log("Migrating %s content types", meta_type)
            brains = catalog.searchResults(meta_type=meta_type)

            # Looping on items
            for brain in brains:
                brain_path = brain.getPath()
                try:
                    item = brain.getObject()
                except Exception, e:
                    LOG_WARNING("Catalog mismatch on %s", brain_path, exc_info=True)
                    continue
                if item is None:
                    LOG_WARNING("Catalog mismatch on %s", brain_path)
                    continue
                item_changed = False
                self.log("Will (try to) migrate fields of %s", brain_path)

                # Looping on fields
                for fieldname, former_storage in patched_fields.items():
                    try:
                        value = former_storage.get(fieldname, item)
                    except AttributeError, e:
                        # Optional empty value -> no migration required
                        continue

                    field = item.getField(fieldname)

                    # Trying to get the mime type
                    try:
                        if hasattr(value, 'content_type'):
                            mimetype = value.content_type
                        else:
                            mimetype = field.getContentType(item)
                    except AttributeError, e:
                        self.log("Can't guess content type of '%s', set to '%s'",
                                 brain_path, UNKNOWN_MIMETYPE)
                        mimetype = UNKNOWN_MIMETYPE
                    
                        mimetype = value.content_type
                    filename = getattr(value, 'filename', None) or item.getId()
                    if filename and (mimetype == UNKNOWN_MIMETYPE):
                        
                        mti = mimetypes_registry.lookupExtension(filename)
                        if mti and (len(mti.mimetypes) > 0):
                            mimetype = mti.mimetypes[0]

                    if isinstance(value, File):
                        unwrapped_value = value.data
                    else:
                        unwrapped_value = str(value)
                    try:
                        # Making a BaseUnit may fail when AT stupidly tries to
                        # guess the text encoding of a binary file!!
                        data = BaseUnit(
                            fieldname,
                            unwrapped_value,
                            instance=item,
                            filename=filename,
                            mimetype=mimetype,
                            )
                    except Exception, e:
                        LOG_ERROR("Migrating %s failed on field %s trying to create its BaseUnit",
                                  brain_path, fieldname,
                                  exc_info=True)
                        continue
                    try:
                        field.set(item, data)
                    except Exception, e:
                        LOG_ERROR("Migrating %s failed on field %s",
                                  brain_path, fieldname,
                                  exc_info=True)
                        continue

                    # Cleaning former storage
                    former_storage.unset(fieldname, item)

                    if mimetype != UNKNOWN_MIMETYPE and hasattr(field, 'setContentType'):
                        # Sometimes AT sucks, we need to say twice the mimetype
                        field.setContentType(item, mimetype)

                    # Removing empty files
                    if field.get_size(item) == 0:
                        field.set(item, 'DELETE_FILE')
                    self.log("Field %s of %s successfully migrated",
                             fieldname, brain_path)
                    item_changed = True
                # /for fieldname...
                if item_changed:
                    self.commit()
            # /for brain...
        # /for content_class
        self.log("Migration ends. %s items migrated", self.changed_items)
        return self.changed_items


    def migrateFromFSS(self):
        """Do migrations from FSS
        """
        # Nothing at the moment. In a certain future...
        self.log("Starting migrations from FSS")
        raise NotImplementedError("Migration from FSS not yet implemented")
        return self.changed_items
