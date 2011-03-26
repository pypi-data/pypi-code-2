##    pywebsite - Python Website Library
##    Copyright (C) 2009, 2010 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com
"""
Using sqlite3 and the pickle module for a simple key value store,
where the keys are text and the values are pickled objects.

Compatible with python2.6 and python3.1 and python2.5 (with pysqlite2).

>>> db = SQLPickle()
>>> db.save('key', 'value')
>>> db.get('key')
'value'


sqlite3:
    http://docs.python.org/3.1/library/sqlite3.html
pickle:
    http://docs.python.org/3.1/library/pickle.html


"""

import sys
try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3

# for pypy, since the sqlite3 package is empty... but they have a pysqlite2.
if not hasattr(sqlite3, "register_converter"):
    from pysqlite2 import dbapi2 as sqlite3


try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import UserDict
    UserDict = UserDict.UserDict
except ImportError:
    import collections
    UserDict = collections.UserDict


serialiser = pickle
sqlite3.register_converter("pickle", serialiser.loads)

#sqlite3.PARSE_DECLTYPES = 1
#sqlite3.PARSE_COLNAMES = 2

import threading
try:
    import thread
except ImportError:
    thread = None


def _get_thread_id():
    """ returns the current thread id.
    """
    if thread:
        return thread.get_ident()
    else:
        return threading.current_thread().ident



def deserialise(data):
    return data
    #return serialiser.loads(str(data))


class SQLPickle(object):

    def __init__(self, database = ':memory:', table_name = 'key_values'):
        self.open(database, table_name)

    def _connect(self, **kwargs):
        detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        kwargs['detect_types'] = detect_types
        self._conn = sqlite3.connect(**kwargs)

    def _sanitise_table_name(self, v):
        """
        """
        unsafe_chars = ";?/\'\""
        for c in unsafe_chars:
            if c in v:
                raise ValueError("unsafe char :%s: in table name :%s:" % (c, v))
        return v


    def open(self, database = ':memory:', table_name = 'key_values'):
        """open() opens the database in memory.
           open(filename) opens the database at the given filename.
           open(':memory:') opens an in memory database.
           open(table_name = 'key_values') opens the database and 
               uses the given table name.
        """

        self._table_name = self._sanitise_table_name(table_name)
        self._database = database
        self._thread_id = _get_thread_id()

        self._connect(database=database)
        self._cursor = self._conn.cursor()
        # fields by name, comment out for normal rows.
        self._cursor.row_factory = sqlite3.Row

        q = """create table %s (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  key text,
                  value pickle,
                  UNIQUE (key)
               );
            """ % self._table_name
        try:
            self._conn.execute(q)
        except sqlite3.OperationalError:
            pass
            # the table most likely already exists.

        self._conn.commit()

    def _check_connection(self):
        """
        """
        if self._thread_id != _get_thread_id():
            # reopen the db.
            self.open(self._table_name, self._database)


    def save(self, key, value, commit = True):
        """ save(key, value) adds the value for the given key.
            Overwrites any existing keys value if there is already one.

            Note, does not commit automatically.
        """
        self._check_connection()

        # use the highest and fastest protocol available.
        data_string = sqlite3.Binary( serialiser.dumps(value, 2) )
        try:
            q = "insert into %s values (null, ?, ?)" % self._table_name
            self._conn.execute(q, (key, data_string))
        except sqlite3.IntegrityError:
            # update instead
            q = "update %s set value = ? where key = ?" % self._table_name
            self._conn.execute(q, (data_string, key))
        if commit:
            self._conn.commit()

    def get(self, key, default = None):
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        self._check_connection()

        q = "select * from %s where key = ?" % self._table_name
        arow = self._cursor.execute(q, (key,)).fetchone()
        if arow is None:
            return default
        return deserialise( arow['value'] )

    def keys(self):
        """ keys() returns a generator of keys.
        """
        self._check_connection()
        q = "select key from %s" % self._table_name
        rows = self._cursor.execute(q).fetchall()
        #return (deserialise(row['key']) for row in rows)
        return [deserialise(row['key']) for row in rows]

    def update(self, E, **F):
        """ D.update(E, **F) -> None.  Update D from dict/iterable E and F.
            If E has a .keys() method, does:     for k in E: D[k] = E[k]
            If E lacks .keys() method, does:     for (k, v) in E: D[k] = v
            In either case, this is followed by: for k in F: D[k] = F[k]
        """
        self._check_connection()
        # TODO: could optimize this to do one SQL call rather than many.
        if hasattr(E, 'keys'):
            for k in E: 
                #D[k] = E[k]
                self.save(k, E[k], False)
        else:
            for (k, v) in E: 
                #D[k] = v
                self.save(k, v, False)

        for k in F: 
            self.save(k, F[k], False)
        
        self._conn.commit()




    def items(self):
        """ items() returns a generator of (key,value) pairs.
        """
        self._check_connection()
        q = "select * from %s" % self._table_name
        rows = self._cursor.execute(q).fetchall()
        return ((deserialise(row['key']), deserialise(row['value'])) for row in rows)


    def values(self):
        """ values() returns a generator of values.
        """
        self._check_connection()
        q = "select * from %s" % self._table_name
        rows = self._cursor.execute(q).fetchall()
        return (deserialise(row['value']) for row in rows)



    def pop(self, key, default = None):
        """ D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
            If key is not found, d is returned if given, otherwise KeyError is raised
        """
        self._check_connection()

        value = self.get(key, KeyError)
        if value is KeyError:
            raise KeyError(key);

        q = "delete from %s where key = ?" % self._table_name
        self._cursor.execute(q, (key,))
        return value


    def commit(self):
        """commit() commits the changes.
        """
        self._check_connection()
        self._conn.commit()

    def rollback(self):
        """rollback() rolls back the changes.
        """
        self._check_connection()
        self._conn.rollback()

    def close(self):
        """close() closes the database connection.
        """
        self._check_connection()
        self._conn.close()


    def __repr__(self):
        if hasattr(self, "_no_unicode_strings"):
            return repr(dict([(str(k), v) for k,v in self.items()]))
        else:
            return repr(dict(self.items()))

