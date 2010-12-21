"""A watchdog for changed files and directories.
"""
##
## iowatchdog.py
## Login : <uli@pu.smp.net>
## Started on  Tue Apr 20 17:16:22 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
import re
from pysqlite2 import dbapi2 as sqlite3
from ulif.pynotify import FILE_TYPE
from ulif.pynotify import ADDED, MODIFIED, DELETED
from ulif.pynotify.sqlite import SQLiteFSWalker as FSWalker
from odls.client.logger import get_component_logger

class ODLSIOWatcher(object):
    """Watch filesystem for changes and notify of changes.
    """

    def __init__(self, app):
        self.app = app
        self.logger = get_component_logger(self.app.config, 'iowatchdog')
        self.logger.debug('Initializing IO watchdog')
        self.options = self.app.config.options
        self.db = self.options.dbfile
        self.blacklist_expr = []
        for expr in self.options.watch_blacklist:
            expr = expr.replace('.', '\.')
            expr = expr.replace('*', '.*')
            expr = expr.replace('?', '.')
            expr = '^%s$' % (expr,)
            self.blacklist_expr.append(expr)
        return

    def stop(self):
        """Stop the IO watcher.

        Does nothing currently.
        """
        pass

    def getChanges(self):
        """Search filesystem for changes since a given timestamp.

        Returns an iterator of :class:`ulif.pynotify.base.FSChange`
        objects to signal any changes in filesystem.

        Changed objects are *not* returned if:

        * they are directories

        * their basename matches some expression in the blacklist
          (see :meth:`inBlacklist`).
        
        """
        self.logger.debug('IOWatcher: look for filesystem changes')
        walker = FSWalker(self.db)
        for path in self._getPathsToExamine():
            self.logger.debug('IOWatcher: Examine changes in %s' % path)
            for change in walker.walk(path):
                if change.filetype is not FILE_TYPE:
                    # Only signal file changes, not directory changes...
                    continue
                if self.inBlacklist(change.basename):
                    continue
                yield change
        self.logger.debug('IOWatcher: finished run.')

    def inBlacklist(self, filename):
        """Determine whether a filename is blacklisted.

        Blacklisted filenames are listed in the ``WATCH_BLACKLIST``
        setting in the configuration. This setting is a list of
        expressions with '*' and '?' as placefolders.

        Matches are performed against the whole filename (including
        the path, if given).
        """
        for expr in self.blacklist_expr:
            if re.match(expr, filename):
                return True
        return False
        
    def _getPathsToExamine(self):
        """Get a generator of all paths to watch, defined in config.
        """
        options = self.app.config.options
        for filepath in options.watch_files:
            path = filepath
            yield path
        for dirpath in options.watch_folders:
            path = dirpath
            yield path
