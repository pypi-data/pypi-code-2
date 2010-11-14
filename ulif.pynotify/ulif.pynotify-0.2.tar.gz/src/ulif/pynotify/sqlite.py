##
## sqlite.py
## Login : <uli@pu.smp.net>
## Started on  Mon Oct 25 15:02:54 2010 Uli Fouquet
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
"""SQLite3 support for file walkers.

See: http://code.google.com/p/pysqlite/source/browse/misc/patterns.py?r=51ab37bca8bf1e56d18df81820e60bbc3aacf1ea

.. versionadded:: 0.2

"""
import os
from datetime import datetime
from ulif.pynotify.base import FSWalker, FSChange
from ulif.pynotify.base import (
    NONE, ADDED, MODIFIED, DELETED, UNKNOWN_TYPE, FILE_TYPE, DIR_TYPE
    )
from pysqlite2 import dbapi2 as sqlite3
from pysqlite2.dbapi2 import OperationalError

FLAGS=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES

class SQLiteFSWalker(FSWalker):
    """A file walker with SQLite support.

    Different to base file walkers the :class:`SQLiteFSWalker` stores
    results of filetree walks in a SQLite database. As a persistent
    file walker it can make assumptions about added and deleted files.

    The database is opened using the given `connection_string`.

    If you pass a path, the database will be created (if it does not
    exist yet) or reused.
    
    In the database we use a table called ``filechanges`` which is
    expected to have the following format:

    =========== ============ ===================
    Column      Type         Attributes/Remarks
    =========== ============ ===================
    id          integer      primary key
    ----------- ------------ -------------------
    path        text         Absolute path
    ----------- ------------ -------------------
    status      integer      Filechange status
    ----------- ------------ -------------------
    ts          datetime     Timestamp
    =========== ============ ===================

    Furthermore we create a unique index idx_path on ``path`` column
    and set the case_sensitive_like pragma to true, to get
    case-sensitive LIKE operators.
    
    If the table does not exist already, it will be created on
    instantiation time of the class.
    """
    
    #: The string to connect to SQLite DB
    connection_string = None
    
    def __init__(self, connection_string=':memory:'):
        """A file walker that supports SQLite to store results.
        """
        self.connection_string = connection_string
        conn = sqlite3.connect(self.connection_string, detect_types=FLAGS)
        self.conn = conn
        cur = conn.cursor()
        self.execute(cur, 'pragma case_sensitive_like = 1')
        self.executescript(
                cur,
                """CREATE table IF NOT EXISTS filechanges (
                       id INTEGER PRIMARY KEY,
                       path TEXT UNIQUE COLLATE BINARY,
                       status INTEGER,
                       ts TIMESTAMP);
                   CREATE UNIQUE INDEX IF NOT EXISTS
                       idx_path ON filechanges(path);
                 """)
        return

    def _execute(self, func, statement, args=None):
        """Execute the SQL statement with args on cursor.
        """
        try:
            if args is not None:
                func(statement, args)
            else:
                func(statement)
        except:
            self.conn.rollback()
            raise
        finally:
            self.conn.commit()
        return

    def execute(self, cursor, statement, args=()):
        """Execute the SQL `statement` with `args` on `cursor`.

        Safe SQL execution of the given SQL `statement`. Performs a
        rollback if unsuccessful and always commits.
        """
        self._execute(cursor.execute, statement, args)
        return

    def executescript(self, cursor, script):
        """Execute the SQL script with args on cursor.
        """
        self._execute(cursor.executescript, script, None)
        return
            
    def walk(self, root_dir):
        """Walk the filetree rooted at `root_dir` and message changes.

        Changes are files, modified in time elapsed since stored
        `timestamp` of ``root_dir`` (:data:`ulif.pynotify.MODIFIED`),
        files that are not yet in the database
        (:data:`ulif.pynotify.ADDED`), and files that were in the
        database but cannot be found in filesystem anymore
        (:data:`ulif.pynotify.DELETED`),.

        Returns a generator of tuples, containing :class:`FSChange`
        objects and a timestamp as `datetime.datetime` object, giving
        the datetime of last modification (if `ADDED` or `MODIFIED`)
        or current datetime (if DELETED).

        The `root_dir`, despite of its name can also be a regular
        file.
        """
        cur1 = self.conn.cursor()
        cur2 = self.conn.cursor()
        root_dir = os.path.abspath(root_dir)
        for change in self._walk(root_dir):
            yield change
        # Find deleted files...
        self.execute(
            cur1,
            'SELECT * FROM filechanges WHERE path LIKE "%s%%"' % (
                root_dir,)
            )
        for result in cur1:
            id, path, changetype, timestamp = result
            if os.path.exists(path):
                continue
            if changetype is DELETED:
                # Change already set...
                continue
            filechange = FSChange(path, changetype=DELETED)
            self.execute(
                cur2,
                'REPLACE INTO filechanges(path, status, ts) VALUES (?, ?, ?)',
                (path, DELETED, datetime.now())
                )
            yield filechange
        pass

    def _walk(self, root_dir):
        conn = self.conn
        cur = conn.cursor()
        status, timestamp = self._checkStatus(root_dir)
        if status is not NONE:
            values = (root_dir, status, timestamp)
            self.execute(
                cur,
                'REPLACE INTO filechanges(path, status, ts) VALUES (?, ?, ?)',
                values)
            yield FSChange(root_dir, changetype=status)
        if os.path.isdir(root_dir):
            for filename in os.listdir(root_dir):
                fullpath = os.path.join(root_dir, filename)
                for x in self._walk(fullpath):
                    yield x


    def getTimeStamp(self, path):
        """Get timestamp for path.

        Returns modification time of ``path`` as `datetime.datetime`
        object.
        """
        try:
            mtime = os.stat(path).st_mtime
            return datetime.fromtimestamp(mtime)
        except OSError:
            pass
        return False

    def _checkStatus(self, path):
        """Check whether file in `path` was changed since timestamp.

        The timestamp is read from the database.

        If there is not entry for `path` in the database, ``ADDED`` is
        returned.

        If the file cannot be accessed, ``DELETED`` is returned.

        Otherwise ``NONE`` or ``MODIFIED`` is returned depending on
        comparison of the timestamp in database and the actual one.

        Returns one of the statuses ``ADDED``, ``MODIFIED``, etc. and
        a timestamp tuple.
        """
        cur = self.conn.cursor()
        self.execute(
            cur,
            'SELECT * FROM filechanges WHERE path=? LIMIT 1', (path,)
            )
        result = list(cur)
        timestamp_curr = self.getTimeStamp(path)
        if len(result) == 0 and timestamp_curr is not False:
            return (ADDED, timestamp_curr)
        if timestamp_curr is False:
            return (DELETED, None)
        result = result[0]
        if result[2] is DELETED:
            # If this entry was deleted in a previous run then it is now
            # not modified but added...
            return (ADDED, timestamp_curr)
        if timestamp_curr <= result[3]:
            return (NONE, result[3])
        return (MODIFIED, timestamp_curr)
