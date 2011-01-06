#!/usr/bin/python
from hashdb_output import log
import sqlite3 as sql
from hashdb_config_base import CombineDB
from collections import namedtuple
import os

def count_components(path):
    '''Returns the number of components in the given path'''
    return path.count('/')

class HashDatabase(object):
    def __init__(self, filename):
        object.__init__(self)

        self._filename = filename
        self._combines = []
        self._mark = None
        self._conn = None

    def add_combine(self, combine):
        self._combines.append(combine)
    def add_combines(self, combines):
        self._combines.extend(combines)

    @property
    def connection(self):
        return self._conn

    def open(self):
        # Open primary database
        try:
            conn = sql.connect(self._filename)
            conn.row_factory = sql.Row
            conn.text_factory = str
            conn.create_function('count_components', 1, count_components)
            self._create_schema(conn)
        except OSError, ex:
            log.error('error: Unable to open primary database (%s): %s' % (self._filename, ex))
            return False
        except sql.Error, ex:
            log.error('error: Unable to open primary database (%s): %s' % (self._filename, ex))
            return False

        # Attach secondary databases
        for i, combine in enumerate(self._combines):
            try:
                alias = self._dbalias(i)
                with conn:
                    conn.execute(
                        r"""ATTACH ? as %s""" % alias,
                        (combine.database,)
                    )
            except OSError, ex:
                log.error('error: Unable to open secondary database (%s): %s' % (combine.database, ex))
                return False
            except sql.Error, ex:
                log.error('error: Unable to open secondary database (%s): %s' % (combine.database, ex))
                return False

        # Create combined view
        try:
            self._create_combined(conn)
        except sql.Error, ex:
            log.error('error: Unable to create combined database view: %s' % ex)
            return False

        # Create working tables
        try:
            self._create_working(conn)
        except sql.Error, ex:
            log.error('error: Unable to create working tables: %s' % ex)
            return False

        '''
        import time
        import random
        with conn:
            conn.execute('INSERT OR REPLACE INTO hashtab (path, hash, size, time, mark) VALUES (?, ?, ?, ?, ?)', ('/test', '1234', 1234, random.randint(1,1000), time.time()))
        '''

        self._conn = conn
        return True

    def _create_basic_schema(self, conn, name, temporary=False):
        primary  =  'NOT NULL' if temporary else 'PRIMARY KEY ASC'
        temporary = 'TEMPORARY' if temporary else ''

        with conn:
            conn.executescript(r"""
                CREATE %(temporary)s TABLE IF NOT EXISTS %(name)s (
                    path TEXT %(primary)s,
                    hash TEXT NOT NULL,
                    size LONG NOT NULL,
                    time LONG NOT NULL,
                    mark LONG NOT NULL
                );

                CREATE INDEX IF NOT EXISTS %(name)s_by_path ON %(name)s (
                    path
                );
                CREATE INDEX IF NOT EXISTS %(name)s_by_hash ON %(name)s (
                    hash
                );
                CREATE INDEX IF NOT EXISTS %(name)s_by_size ON %(name)s (
                    size
                );
                CREATE INDEX IF NOT EXISTS %(name)s_by_hash_size ON %(name)s (
                    hash,
                    size
                );
                CREATE INDEX IF NOT EXISTS %(name)s_by_size_time ON %(name)s (
                    size,
                    time
                );
                CREATE INDEX IF NOT EXISTS %(name)s_by_hash_size_time ON %(name)s (
                    hash,
                    size,
                    time
                );
                CREATE INDEX IF NOT EXISTS %(name)s_by_mark ON %(name)s (
                    mark
                );
            """ % { 'temporary':temporary, 'primary':primary, 'name':name })

    def _dbalias(self, i):
        return 'remotedb%02d' % i

    def _create_combined(self, conn):
        self._create_basic_schema(conn, 'combinedtab', True)

        selects = []
        argmap  = {}

        selects.append(r"""
            SELECT
                path,
                hash,
                size,
                time,
                mark
            FROM
                hashtab
        """)

        for i, combine in enumerate(self._combines):
            local = combine.local
            if local != None:
                local = os.path.abspath(local)
            else:
                local = '/'
            remote = combine.remote
            if remote == None:
                remote = '/'

            if (local == '/') and (remote == '/'):
                selects.append(r"""
                    SELECT
                        path,
                        hash,
                        size,
                        time,
                        0 as mark
                    FROM
                        %s.hashtab
                """ % self._dbalias(i))
            else:
                selects.append(r"""
                    SELECT
                        :%(name)s_local || substr(path, :%(name)s_remote_len) as path,
                        hash,
                        size,
                        time,
                        0 as mark
                    FROM
                        %(name)s.hashtab
                    WHERE
                        (path = :%(name)s_remote) OR
                        (substr(path, 1, :%(name)s_remote_len + 1) = :%(name)s_remote || '/')
                """ % {'name': self._dbalias(i)})

                argmap.update({
                    '%s_local'      % self._dbalias(i): local,
                    '%s_remote'     % self._dbalias(i): remote,
                    '%s_remote_len' % self._dbalias(i): len(remote),
                })

        statement = r"""
            INSERT OR IGNORE INTO combinedtab
        """ +\
        r"""
            UNION
        """.join(selects) +\
        r"""
            ORDER BY
                path,
                mark DESC
        """

        with conn:
            conn.execute(statement, argmap)

    def _create_working(self, conn):
        with conn:
            conn.executescript(r"""
                CREATE TEMPORARY TABLE IF NOT EXISTS dirtab (
                    path TEXT PRIMARY KEY
                );
            """)

    def _create_schema(self, conn):
        self._create_basic_schema(conn, 'hashtab', False)

        with conn:
            conn.executescript(r"""
                CREATE TABLE IF NOT EXISTS marktab (
                    mark INTEGER PRIMARY KEY AUTOINCREMENT,
                    time LONG
                );
            """)

    @property
    def mark(self):
        if self._mark == None:
            with self._conn:
                self._mark = self._conn.execute(r"""INSERT INTO marktab (time) VALUES (strftime('%s','now'))""").lastrowid
        return self._mark

    def _ismatch(self, row, stat):
        return (row['time'] == stat.st_mtime) and (row['size'] == stat.st_size)

    def path_mark(self, path):
        with self._conn as conn:
            conn.execute(r"""UPDATE hashtab SET mark=? WHERE path=?""", (self.mark, path))
    def path_update(self, path, stat, hash):
        self.path_update_direct(path, stat.st_size, stat.st_mtime, hash)
    def path_update_direct(self, path, size, time, hash):
        with self._conn as conn:
            conn.execute(r"""UPDATE hashtab SET hash=?, size=?, time=?, mark=? WHERE path=?""", (hash, size, time, self.mark, path))

    def path_dirdone(self, path):
        row = self._conn.execute(r"""SELECT * FROM dirtab WHERE path=?""", (path,)).fetchone()
        if not row:
            with self._conn as conn:
                conn.execute(r"""INSERT INTO dirtab (path) VALUES (?)""", (path,))
            return False
        else:
            return True

    def path_hash(self, path, stat):
        row = self._conn.execute(r"""SELECT * FROM hashtab WHERE path=?""", (path,)).fetchone()
        if row:
            if row['mark'] == self.mark:
                return row['hash'] # already upto date
            if self._ismatch(row, stat):
                self.path_mark(path)
                return row['hash'] # old hash is still valid

        for row in self._conn.execute(r"""SELECT * FROM combinedtab WHERE path=?""", (path,)):
            if self._ismatch(row, stat):
                self.path_update_direct(path=path, hash=row['hash'], size=row['size'], time=row['time'])
                return row['hash'] # hash from combined database is valid

        return None

    def path_discard_unmarked(self, path):
        ##self._conn.execute(r"""DELETE FROM hashtab WHERE mark=?""",  (self.mark,))
        pass

    def path_insert(self, path, stat, hash):
        with self._conn as conn:
            conn.execute(r"""INSERT OR REPLACE INTO hashtab (path, hash, size, time, mark) VALUES (?, ?, ?, ?, ?)""", (path, hash, stat.st_size, stat.st_mtime, self.mark))

    def path_findall(self, path):
        for row in self._conn.execute(r"""SELECT * FROM hashtab WHERE path=? UNION SELECT * FROM combinedtab WHERE path=? ORDER BY path, mark DESC""", (path,path)):
            yield row

    def path_findroot(self, path):
        for row in self._conn.execute(r"""
                SELECT * FROM hashtab WHERE (path=:path) OR (substr(path,1,:path_len + 1) == :path || '/')
                UNION
                SELECT * FROM combinedtab WHERE (path=:path) OR (substr(path,1,:path_len + 1) == :path || '/')
            """, {'path':path, 'path_len':len(path)}):
            yield row



if __name__ == '__main__':
    from hashdb_config_base import CombineDB

    dbB = HashDatabase('test/secondary.db')
    dbB.open()

    dbC = HashDatabase('test/ternary.db')
    dbC.open()

    dbA = HashDatabase('test/primary.db')
    dbA.add_combine(CombineDB('', 'test/secondary.db', ''))
    dbA.add_combine(CombineDB('', 'test/ternary.db', ''))
    dbA.open()

    for row in dbA._conn.execute('SELECT * FROM combinedtab'):
        print row
