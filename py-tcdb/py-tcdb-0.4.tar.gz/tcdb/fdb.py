# -*- coding: utf-8 -*-
# Tokyo Cabinet Python ctypes binding.

"""
FDB is an implementation of bsddb-like API for Tokyo Cabinet
fixed-length database.

We need to import 'FDB' class, and use it like that:

>>> from tcdb.fdb import FDB

>>> db = FDB()             # Create a new database object
>>> db.open('casket.tch')  # By default create it if don't exist

>>> db.put(1, "hop")
True
>>> db.put(2, "step")
True
>>> db.put(3, "jump")
True

>>> db.get(1)
'hop'

>>> db.close()

"""

import ctypes
import datetime

import tc
import util


# enumeration for additional flags
FOPEN   = 1 << 0              # whether opened
FFATAL  = 1 << 1              # whether with fatal error

# enumeration for open modes
OREADER = 1 << 0              # open as a reader
OWRITER = 1 << 1              # open as a writer
OCREAT  = 1 << 2              # writer creating
OTRUNC  = 1 << 3              # writer truncating
ONOLCK  = 1 << 4              # open without locking
OLCKNB  = 1 << 5              # lock without blocking
OTSYNC  = 1 << 6              # synchronize every transaction

# enumeration for ID constants
IDMIN   = -1                  # minimum number
IDPREV  = -2                  # less by one than the minimum
IDMAX   = -3                  # maximum number
IDNEXT  = -4                  # greater by one than the miximum


class FDBSimple(object):
    def __init__(self):
        """Create a fixed-length database object."""
        self.db = tc.fdb_new()

    def __del__(self):
        """Delete a fixed-length database object."""
        tc.fdb_del(self.db)

    def setmutex(self):
        """Set mutual exclusion control of a fixed-length database
        object for threading."""
        return tc.fdb_setmutex(self.db)

    def tune(self, width=0, limsiz=0):
        """Set the tuning parameters of a fixed-length database
        object."""
        result = tc.fdb_tune(self.db, width, limsiz)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def open(self, path, omode=OWRITER|OCREAT, width=0, limsiz=0):
        """Open a database file and connect a fixed-length database
        object."""
        self.tune(width, limsiz)

        if not tc.fdb_open(self.db, path, omode):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))

    def close(self):
        """Close a fixed-length database object."""
        result = tc.fdb_close(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __setitem__(self, key, value):
        """Store any Python object into a fixed-length database
        object."""
        return self.put(key, value)

    def put(self, key, value):
        """Store a string record into a fixed-length database object."""
        result = tc.fdb_put3(self.db, key, value)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def putkeep(self, key, value):
        """Store a new string record into a fixed-length database
        object."""
        return tc.fdb_putkeep3(self.db, key, value)

    def putcat(self, key, value):
        """Concatenate a string value with a decimal key in a
        fixed-length database object."""
        result = tc.fdb_putcat3(self.db, key, value)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __delitem__(self, key):
        """Remove a Python object of a fixed-length database object."""
        return self.out(key)

    def out(self, key):
        """Remove a record with a decimal key of a fixed-length
        database object."""
        result = tc.fdb_out3(self.db, key)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __getitem__(self, key):
        """Retrieve a Python object in a fixed-length database object."""
        return self._getitem(key)

    def _getitem(self, key):
        """Retrieve a string record with a decimal key in a
        fixed-length database object."""
        value = tc.fdb_get3(self.db, key)
        if not value:
            raise KeyError(key)
        return value.value

    def get(self, key, default=None):
        """Retrieve a string record with a decimal key in a
        fixed-length database object."""
        try:
            value = self._getitem(key)
        except KeyError:
            value = default
        return value

    def vsiz(self, key):
        """Get the size of the string value with a decimal key in a
        fixed-length database object."""
        result = tc.fdb_vsiz3(self.db, key)
        if result == -1:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def keys(self):
        """Get all the keys of a fixed-length database object."""
        return list(self.iterkeys())

    def iterkeys(self):
        """Iterate for every key in a fixed-length database object."""
        if not tc.fdb_iterinit(self.db):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        while True:
            key = tc.fdb_iternext3(self.db)
            if not key:
                break
            yield key.value

    def values(self):
        """Get all the values of a fixed-length database object."""
        return list(self.itervalues())

    def itervalues(self):
        """Iterate for every value in a fixed-length database object."""
        if not tc.fdb_iterinit(self.db):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        while True:
            key = tc.fdb_iternext3(self.db)
            if not key:
                break
            value = tc.fdb_get3(self.db, key)
            yield value.value

    def items(self):
        """Get all the items of a fixed-length database object."""
        return list(self.iteritems())

    def iteritems(self):
        """Iterate for every key / value in a fixed-length database
        object."""
        if not tc.fdb_iterinit(self.db):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        while True:
            key = tc.fdb_iternext3(self.db)
            if not key:
                break
            value = tc.fdb_get3(self.db, key)
            yield (key.value, value.value)

    def __iter__(self):
        """Iterate for every key in a fixed-length database object."""
        return self.iterkeys()

    def range(self, lower, upper, max_=-1):
        """Get range matching ID numbers in a fixed-length database
        object."""
        tclist_objs = tc.fdb_range3(self.db, lower, upper, max_)
        if not tclist_objs:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return util.deserialize_tclist(tclist_objs, str)

    def sync(self):
        """Synchronize updated contents of a fixed-length database object with
        the file and the device."""
        result = tc.fdb_sync(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def optimize(self, width=None, limsiz=None):
        """Optimize the file of a fixed-length database object."""
        kwargs = dict([x for x in (('width', width),
                                   ('limsiz', limsiz)) if x[1]])
        result = tc.fdb_optimize(self.db, **kwargs)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def vanish(self):
        """Remove all records of a fixed-length database object."""
        result = tc.fdb_vanish(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def copy(self, path):
        """Copy the database file of a fixed-length database object."""
        result = tc.fdb_copy(self.db, path)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def tranbegin(self):
        """Begin the transaction of a fixed-length database object."""
        result = tc.fdb_tranbegin(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def trancommit(self):
        """Commit the transaction of a fixed-length database object."""
        result = tc.fdb_trancommit(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def tranabort(self):
        """Abort the transaction of a fixed-length database object."""
        result = tc.fdb_tranabort(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __enter__(self):
        """Enter in the 'with' statement and begin the transaction."""
        self.tranbegin()
        return self

    def __exit__(self, type, value, traceback):
        """Exit from 'with' statement and ends the transaction."""
        if type is None:
            self.trancommit()
        else:
            self.tranabort()

    def path(self):
        """Get the file path of a fixed-length database object."""
        result = tc.fdb_path(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __len__(self):
        """Get the number of records of a fixed-length database object."""
        return tc.fdb_rnum(self.db)

    def fsiz(self):
        """Get the size of the database file of a fixed-length database
        object."""
        result = tc.fdb_fsiz(self.db)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def setecode(self, ecode, filename, line, func):
        """Set the error code of a fixed-length database object."""
        tc.fdb_setecode(self.db, ecode, filename, line, func)

    def setdbgfd(self, fd):
        """Set the file descriptor for debugging output."""
        tc.fdb_setdbgfd(self.db, fd)

    def dbgfd(self):
        """Get the file descriptor for debugging output."""
        return tc.fdb_dbgfd(self.db)

    def hasmutex(self):
        """Check whether mutual exclusion control is set to a fixed-length
        database object."""
        return tc.fdb_hasmutex(self.db)

    def memsync(self, phys):
        """Synchronize updating contents on memory of a fixed-length database
        object."""
        result = tc.fdb_memsync(self.db, phys)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def width(self):
        """Get the width of the value of each record of a fixed-length
        database object."""
        return tc.fdb_width(self.db)

    def limsiz(self):
        """Get the limit file size of a fixed-length database
        object."""
        return tc.fdb_limsiz(self.db)

    def limid(self):
        """Get the limit ID number of a fixed-length database object."""
        return tc.fdb_limid(self.db)

    def inode(self):
        """Get the inode number of the database file of a fixed-length
        database object."""
        return tc.fdb_inode(self.db)

    def mtime(self):
        """Get the modification time of the database file of a fixed-length
        database object."""
        return datetime.datetime.fromtimestamp(tc.fdb_mtime(self.db))

    def omode(self):
        """Get the connection mode of a fixed-length database object."""
        return tc.fdb_omode(self.db)

    def type(self):
        """Get the database type of a fixed-length database object."""
        return tc.fdb_type(self.db)

    def flags(self):
        """Get the additional flags of a fixed-length database object."""
        return tc.fdb_flags(self.db)

    def opaque(self):
        """Get the pointer to the opaque field of a fixed-length database
        object."""
        return tc.fdb_opaque(self.db)

    # def putproc(self, key, value, proc, op):
    #     """Store a record into a fixed-length database object with a
    #     duplication handler."""
    #     # See tc.fdb_putproc

    def foreach(self, proc, op):
        """Process each record atomically of a fixed-length database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, str)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, str)
            return proc(int(key), value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.fdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __contains__(self, key):
        """Return True if fixed-length database object has the key."""
        return self.has_key(key)

    def has_key(self, key):
        """Return True if fixed-length database object has the key."""
        return tc.fdb_iterinit4(self.db, key)


class FDB(FDBSimple):
    def __init__(self):
        """Create a fixed-length database object."""
        FDBSimple.__init__(self)

    def put(self, key, value, as_raw=False):
        """Store any Python object into a fixed-length database
        object."""
        (c_value, c_value_len) = util.serialize(value, as_raw)
        result = tc.fdb_put(self.db, key, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def put_str(self, key, value):
        """Store a string record into a fixed-length database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.put(key, value, True)

    def put_unicode(self, key, value):
        """Store an unicode string record into a fixed-length database
        object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.put(key, value, True)

    def put_int(self, key, value):
        """Store an integer record into a fixed-length database
        object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.put(key, value, True)

    def put_float(self, key, value):
        """Store a double precision record into a fixed-length
        database object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.put(key, value, True)

    def putkeep(self, key, value, as_raw=False):
        """Store a new Python object into a fixed-length database
        object."""
        (c_value, c_value_len) = util.serialize(value, as_raw)
        return tc.fdb_putkeep(self.db, key, c_value, c_value_len)

    def putkeep_str(self, key, value):
        """Store a new string record into a fixed-length database
        object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putkeep(key, value, True)

    def putkeep_unicode(self, key, value):
        """Store a new unicode string record into a fixed-length
        database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putkeep(key, value, True)

    def putkeep_int(self, key, value):
        """Store a new integer record into a fixed-length database
        object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putkeep(key, value, True)

    def putkeep_float(self, key, value):
        """Store a new double precision record into a fixed-length
        database object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putkeep(key, value, True)

    def putcat(self, key, value, as_raw=False):
        """Concatenate a Python object value at the end of the
        existing record in a fixed-length database object."""
        (c_value, c_value_len) = util.serialize(value, as_raw)
        result = tc.fdb_putcat(self.db, key, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def putcat_str(self, key, value):
        """Concatenate a string value at the end of the existing
        record in a fixed-length database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putcat(key, value, True)

    def putcat_unicode(self, key, value):
        """Concatenate an unicode string value at the end of the
        existing record in a fixed-length database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putcat(key, value, True)

    def out(self, key):
        """Remove a Python object of a fixed-length database object."""
        result = tc.fdb_out(self.db, key)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def __getitem__(self, key):
        """Retrieve a Python object in a fixed-length database object."""
        result = None
        if isinstance(key, slice):
            start, stop, step = key.indices(self.__len__()+1)
            result = [self._getitem(k) for k in xrange(start, stop, step)]
        else:
            result = self._getitem(key)
        return result

    def _getitem(self, key, as_type=None):
        """Retrieve a Python object in a fixed-length database object."""
        (c_value, c_value_len) = tc.fdb_get(self.db, key)
        if not c_value:
            raise KeyError(key)
        return util.deserialize(c_value, c_value_len, as_type)

    def get(self, key, default=None, as_type=None):
        """Retrieve a Python object in a fixed-length database object."""
        try:
            value = self._getitem(key, as_type)
        except KeyError:
            value = default
        return value

    def get_str(self, key, default=None):
        """Retrieve a string record in a fixed-length database object."""
        return self.get(key, default, str)

    def get_unicode(self, key, default=None):
        """Retrieve an unicode string record in a fixed-length
        database object."""
        return self.get(key, default, unicode)

    def get_int(self, key, default=None):
        """Retrieve an integer record in a fixed-length database
        object."""
        return self.get(key, default, int)

    def get_float(self, key, default=None):
        """Retrieve a double precision record in a fixed-length
        database object."""
        return self.get(key, default, float)

    def vsiz(self, key):
        """Get the size of the value of a Python object in a
        fixed-length database object."""
        result = tc.fdb_vsiz(self.db, key)
        if result == -1:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def iterkeys(self):
        """Iterate for every key in a fixed-length database object."""
        if not tc.fdb_iterinit(self.db):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        while True:
            key = tc.fdb_iternext(self.db)
            if not key:
                break
            yield key

    def values(self, as_type=None):
        """Get all the values of a fixed-length database object."""
        return list(self.itervalues(as_type))

    def itervalues(self, as_type=None):
        """Iterate for every value in a fixed-length database object."""
        if not tc.fdb_iterinit(self.db):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        while True:
            key = tc.fdb_iternext(self.db)
            if not key:
                break
            (c_value, c_value_len) = tc.fdb_get(self.db, key)
            value = util.deserialize(c_value, c_value_len, as_type)
            yield value

    def items(self, as_type=None):
        """Get all the items of a fixed-length database object."""
        return list(self.iteritems(as_type))

    def iteritems(self, as_type=None):
        """Iterate for every key / value in a fixed-length database
        object."""
        if not tc.fdb_iterinit(self.db):
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        while True:
            key = tc.fdb_iternext(self.db)
            if not key:
                break
            (c_value, c_value_len) = tc.fdb_get(self.db, key)
            value = util.deserialize(c_value, c_value_len, as_type)
            yield (key, value)

    def range(self, lower, upper, max_=-1):
        """Get range matching ID numbers in a fixed-length database
        object."""
        return tc.fdb_range(self.db, lower, upper, max_)

    def add_int(self, key, num):
        """Add an integer to a record in a fixed-length database object."""
        assert isinstance(num, int), 'Value is not an integer'
        result = tc.fdb_addint(self.db, key, num)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def add_float(self, key, num):
        """Add a real number to a record in a fixed-length database object."""
        assert isinstance(num, float), 'Value is not a float'
        result = tc.fdb_adddouble(self.db, key, num)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def min(self):
        """Get the minimum ID number of records of a fixed-length
        database object."""
        return tc.fdb_min(self.db)

    def max(self):
        """Get the maximum ID number of records of a fixed-length
        database object."""
        return tc.fdb_max(self.db)

    def foreach(self, proc, op, as_type=None):
        """Process each record atomically of a fixed-length database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, str)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, as_type)
            return proc(int(key), value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.fdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.fdb_errmsg(tc.fdb_ecode(self.db)))
        return result

    def keytoid(self, key):
        """Generate the ID number from arbitrary binary data."""
        (c_key, c_key_len) = util.serialize(key, True)
        return tc.fdb_keytoid(self.db, c_key, c_key_len)

    def has_key(self, key):
        """Return True if fixed-length database object has the key."""
        return tc.fdb_iterinit2(self.db, key)
