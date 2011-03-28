# -*- coding: utf-8 -*-
# Tokyo Cabinet Python ctypes binding.

"""
HDB is an implementation of bsddb-like API for Tokyo Cabinet hash
database.

We need to import 'HDB' class, and use it like that:

>>> from tcdb.hdb import HDB

>>> db = HDB()             # Create a new database object
>>> db.open('casket.tch')  # By default create it if don't exist

>>> db.put("foo", "hop")
True
>>> db.put("bar", "step")
True
>>> db.put("baz", "jump")
True

>>> db.get("foo")
'hop'

>>> db.close()

"""

import ctypes
import datetime

import tc
import util


# enumeration for additional flags
FOPEN    = 1 << 0             # whether opened
FFATAL   = 1 << 1             # whether with fatal error

# enumeration for tuning options
TLARGE   = 1 << 0             # use 64-bit bucket array
TDEFLATE = 1 << 1             # compress each record with Deflate
TBZIP    = 1 << 2             # compress each record with BZIP2
TTCBS    = 1 << 3             # compress each record with TCBS
TEXCODEC = 1 << 4             # compress each record with custom functions

# enumeration for open modes
OREADER  = 1 << 0             # open as a reader
OWRITER  = 1 << 1             # open as a writer
OCREAT   = 1 << 2             # writer creating
OTRUNC   = 1 << 3             # writer truncating
ONOLCK   = 1 << 4             # open without locking
OLCKNB   = 1 << 5             # lock without blocking
OTSYNC   = 1 << 6             # synchronize every transaction


class HDBSimple(object):
    def __init__(self):
        """Create a hash database object."""
        self.db = tc.hdb_new()

    def __del__(self):
        """Delete a hash database object."""
        tc.hdb_del(self.db)

    def setmutex(self):
        """Set mutual exclusion control of a hash database object for
        threading."""
        return tc.hdb_setmutex(self.db)

    def tune(self, bnum=0, apow=-1, fpow=-1, opts=0):
        """Set the tuning parameters of a hash database object."""
        result = tc.hdb_tune(self.db, bnum, apow, fpow, opts)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setcache(self, rcnum=0):
        """Set the caching parameters of a hash database object."""
        result = tc.hdb_setcache(self.db, rcnum)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setxmsiz(self, xmsiz=0):
        """Set the size of the extra mapped memory of a hash database
        object."""
        result = tc.hdb_setxmsiz(self.db, xmsiz)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setdfunit(self, dfunit=0):
        """Set the unit step number of auto defragmentation of a hash
        database object."""
        result = tc.hdb_setdfunit(self.db, dfunit)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def open(self, path, omode=OWRITER|OCREAT, bnum=0, apow=-1, fpow=-1,
             opts=0, rcnum=0, xmsiz=67108864, dfunit=0):
        """Open a database file and connect a hash database object."""
        if bnum or apow >= 0 or fpow >= 0 or opts:
            self.tune(bnum, apow, fpow, opts)
        if rcnum:
            self.setcache(rcnum)
        if xmsiz != 67108864:
            self.setxmsiz(xmsiz)
        if dfunit:
            self.setdfunit(dfunit)

        if not tc.hdb_open(self.db, path, omode):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))

    def close(self):
        """Close a hash database object."""
        result = tc.hdb_close(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __setitem__(self, key, value):
        """Store any Python object into a hash database object."""
        return self.put(key, value)

    def put(self, key, value):
        """Store a string record into a hash database object."""
        # assert isinstance(key, str), 'Key is not a string'
        # assert isinstance(value, str), 'Value is not a string'
        result = tc.hdb_put2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putkeep(self, key, value):
        """Store a new string record into a hash database object."""
        # assert isinstance(key, str), 'Key is not a string'
        # assert isinstance(value, str), 'Value is not a string'
        return tc.hdb_putkeep2(self.db, key, value)

    def putcat(self, key, value):
        """Concatenate a string value at the end of the existing
        record in a hash database object."""
        # assert isinstance(key, str), 'Key is not a string'
        # assert isinstance(value, str), 'Value is not a string'
        result = tc.hdb_putcat2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putasync(self, key, value):
        """Store a string record into a hash database object in
        asynchronous fashion."""
        # assert isinstance(key, str), 'Key is not a string'
        # assert isinstance(value, str), 'Value is not a string'
        result = tc.hdb_putasync2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __delitem__(self, key):
        """Remove a string record of a hash database object."""
        return self.out(key)

    def out(self, key):
        """Remove a string record of a hash database object."""
        # assert isinstance(key, str), 'Key is not a string'
        result = tc.hdb_out2(self.db, key)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __getitem__(self, key):
        """Retrieve a Python object in a hash database object."""
        return self._getitem(key)

    def _getitem(self, key):
        """Retrieve a Python object in a hash database object."""
        value = tc.hdb_get2(self.db, key)
        if not value:
            raise KeyError(key)
        return value.value

    def get(self, key, default=None):
        """Retrieve a Python object in a hash database object."""
        # assert isinstance(key, str), 'Key is not a string'
        try:
            value = self._getitem(key)
        except KeyError:
            value = default
        return value

    def vsiz(self, key):
        """Get the size of the value of a Python object in a hash
        database object."""
        result = tc.hdb_vsiz2(self.db, key)
        if result == -1:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def keys(self):
        """Get all the keys of a hash database object."""
        return list(self.iterkeys())

    def iterkeys(self):
        """Iterate for every key in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            key = tc.hdb_iternext2(self.db)
            if not key:
                break
            yield key.value

    def values(self):
        """Get all the values of a hash database object."""
        return list(self.itervalues())

    def itervalues(self):
        """Iterate for every value in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            key = tc.hdb_iternext2(self.db)
            if not key:
                break
            value = tc.hdb_get2(self.db, key)
            yield value.value

    def items(self):
        """Get all the items of a hash database object."""
        return list(self.iteritems())

    def iteritems(self):
        """Iterate for every key / value in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            key = tc.hdb_iternext2(self.db)
            if not key:
                break
            value = tc.hdb_get2(self.db, key)
            yield key.value, value.value

    def __iter__(self):
        """Iterate for every key in a hash database object."""
        return self.iterkeys()

    def fwmkeys(self, prefix, max_=-1):
        """Get forward matching string keys in a hash database object."""
        tclist_objs = tc.hdb_fwmkeys2(self.db, prefix, max_)
        if not tclist_objs:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return util.deserialize_tclist(tclist_objs, str)

    def sync(self):
        """Synchronize updated contents of a hash database object with
        the file and the device."""
        result = tc.hdb_sync(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def optimize(self, bnum=None, apow=None, fpow=None, opts=None):
        """Optimize the file of a hash database object."""
        kwargs = dict([x for x in (('bnum', bnum),
                                   ('apow', apow),
                                   ('fpow', fpow),
                                   ('opts', opts)) if x[1]])
        result = tc.hdb_optimize(self.db, **kwargs)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def vanish(self):
        """Remove all records of a hash database object."""
        result = tc.hdb_vanish(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def copy(self, path):
        """Copy the database file of a hash database object."""
        result = tc.hdb_copy(self.db, path)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def tranbegin(self):
        """Begin the transaction of a hash database object."""
        result = tc.hdb_tranbegin(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def trancommit(self):
        """Commit the transaction of a hash database object."""
        result = tc.hdb_trancommit(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def tranabort(self):
        """Abort the transaction of a hash database object."""
        result = tc.hdb_tranabort(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
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
        """Get the file path of a hash database object."""
        result = tc.hdb_path(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __len__(self):
        """Get the number of records of a hash database object."""
        return tc.hdb_rnum(self.db)

    def fsiz(self):
        """Get the size of the database file of a hash database
        object."""
        result = tc.hdb_fsiz(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def setecode(self, ecode, filename, line, func):
        """Set the error code of a hash database object."""
        tc.hdb_setecode(self.db, ecode, filename, line, func)

    def settype(self, type_):
        """Set the type of a hash database object."""
        tc.hdb_settype(self.db, type_)

    def setdbgfd(self, fd):
        """Set the file descriptor for debugging output."""
        tc.hdb_setdbgfd(self.db, fd)

    def dbgfd(self):
        """Get the file descriptor for debugging output."""
        return tc.hdb_dbgfd(self.db)

    def hasmutex(self):
        """Check whether mutual exclusion control is set to a hash
        database object."""
        return tc.hdb_hasmutex(self.db)

    def memsync(self, phys):
        """Synchronize updating contents on memory of a hash database
        object."""
        result = tc.hdb_memsync(self.db, phys)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def cacheclear(self):
        """Clear the cache of a hash tree database object."""
        result = tc.hdb_cacheclear(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def bnum(self):
        """Get the number of elements of the bucket array of a hash
        database object."""
        return tc.hdb_bnum(self.db)

    def align(self):
        """Get the record alignment of a hash database object."""
        return tc.hdb_align(self.db)

    def fbpmax(self):
        """Get the maximum number of the free block pool of a a hash
        database object."""
        return tc.hdb_fbpmax(self.db)

    def xmsiz(self):
        """Get the size of the extra mapped memory of a hash database
        object."""
        return tc.hdb_xmsiz(self.db)

    def inode(self):
        """Get the inode number of the database file of a hash
        database object."""
        return tc.hdb_inode(self.db)

    def mtime(self):
        """Get the modification time of the database file of a hash
        database object."""
        return datetime.datetime.fromtimestamp(tc.hdb_mtime(self.db))

    def omode(self):
        """Get the connection mode of a hash database object."""
        return tc.hdb_omode(self.db)

    def type(self):
        """Get the database type of a hash database object."""
        return tc.hdb_type(self.db)

    def flags(self):
        """Get the additional flags of a hash database object."""
        return tc.hdb_flags(self.db)

    def opts(self):
        """Get the options of a hash database object."""
        return tc.hdb_opts(self.db)

    def opaque(self):
        """Get the pointer to the opaque field of a hash database
        object."""
        return tc.hdb_opaque(self.db)

    def bnumused(self):
        """Get the number of used elements of the bucket array of a
        hash database object."""
        return tc.hdb_bnumused(self.db)

    # def setcodecfunc(self, enc, encop, dec, decop):
    #     """Set the custom codec functions of a hash database
    #     object."""
    #     result = tc.hdb_setcodecfunc(self.db, TCCODEC(enc), encop,
    #                                  TCCODEC(dec), decop)
    #     if not result:
    #         raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
    #     return result

    # def codecfunc(self):
    #     """Get the custom codec functions of a hash database
    #     object."""
    #     # See tc.hdb_codecfunc

    def dfunit(self):
        """Get the unit step number of auto defragmentation of a hash
        database object."""
        return tc.hdb_dfunit(self.db)

    def defrag(self, step):
        """Perform dynamic defragmentation of a hash database
        object."""
        result = tc.hdb_defrag(self.db, step)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    # def putproc(self, key, value, proc, op):
    #     """Store a record into a hash database object with a
    #     duplication handler."""
    #     # See tc.hdb_putproc

    def foreach(self, proc, op):
        """Process each record atomically of a hash database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, str)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, str)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.hdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def tranvoid(self):
        """Void the transaction of a hash database object."""
        result = tc.hdb_tranvoid(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __contains__(self, key):
        """Return True if hash database object has the key."""
        return self.has_key(key)

    def has_key(self, key):
        """Return True if hash database object has the key."""
        return tc.hdb_iterinit3(self.db, key)


class HDB(HDBSimple):
    def __init__(self):
        """Create a hash database object."""
        HDBSimple.__init__(self)

    def put(self, key, value, raw_key=False, raw_value=False):
        """Store any Python object into a hash database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.hdb_put(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def put_str(self, key, value, as_raw=False):
        """Store a string record into a hash database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.put(key, value, as_raw, True)

    def put_unicode(self, key, value, as_raw=False):
        """Store an unicode string record into a hash database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.put(key, value, as_raw, True)

    def put_int(self, key, value, as_raw=False):
        """Store an integer record into a hash database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.put(key, value, as_raw, True)

    def put_float(self, key, value, as_raw=False):
        """Store a double precision record into a hash database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.put(key, value, as_raw, True)

    def putkeep(self, key, value, raw_key=False, raw_value=False):
        """Store a new Python object into a hash database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        return tc.hdb_putkeep(self.db, c_key, c_key_len, c_value, c_value_len)

    def putkeep_str(self, key, value, as_raw=False):
        """Store a new string record into a hash database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_unicode(self, key, value, as_raw=False):
        """Store a new unicode string record into a hash database
        object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_int(self, key, value, as_raw=False):
        """Store a new integer record into a hash database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_float(self, key, value, as_raw=False):
        """Store a new double precision record into a hash database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putkeep(key, value, as_raw, True)

    def putcat(self, key, value, raw_key=False, raw_value=False):
        """Concatenate an object value at the end of the existing
        record in a hash database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.hdb_putcat(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putcat_str(self, key, value, as_raw=False):
        """Concatenate a string value at the end of the existing
        record in a hash database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putcat(key, value, as_raw, True)

    def putcat_unicode(self, key, value, as_raw=False):
        """Concatenate an unicode string value at the end of the
        existing record in a hash database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putcat(key, value, as_raw, True)

    def putasync(self, key, value, raw_key=False, raw_value=False):
        """Store a Python object into a hash database object in
        asynchronous fashion."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.hdb_putasync(self.db, c_key, c_key_len, c_value,
                                 c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putasync_str(self, key, value, as_raw=False):
        """Store a string record into a hash database object in
        asynchronous fashion."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putasync(key, value, as_raw, True)

    def putasync_unicode(self, key, value, as_raw=False):
        """Store an unicode string record into a hash database object
        in asynchronous fashion."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putasync(key, value, as_raw, True)

    def putasync_int(self, key, value, as_raw=False):
        """Store an integer record into a hash database object in
        asynchronous fashion."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putasync(key, value, as_raw, True)

    def putasync_float(self, key, value, as_raw=False):
        """Store a double precision record into a hash database object
        in asynchronous fashion."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putasync(key, value, as_raw, True)

    def out(self, key, as_raw=False):
        """Remove a Python object of a hash database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.hdb_out(self.db, c_key, c_key_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def _getitem(self, key, raw_key=False, value_type=None):
        """Retrieve a Python object in a hash database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = tc.hdb_get(self.db, c_key, c_key_len)
        if not c_value:
            raise KeyError(key)
        return util.deserialize(c_value, c_value_len, value_type)

    def get(self, key, default=None, raw_key=False, value_type=None):
        """Retrieve a Python object in a hash database object."""
        try:
            value = self._getitem(key, raw_key, value_type)
        except KeyError:
            value = default
        return value

    def get_str(self, key, default=None, as_raw=False):
        """Retrieve a string record in a hash database object."""
        return self.get(key, default, as_raw, str)

    def get_unicode(self, key, default=None, as_raw=False):
        """Retrieve an unicode string record in a hash database
        object."""
        return self.get(key, default, as_raw, unicode)

    def get_int(self, key, default=None, as_raw=False):
        """Retrieve an integer record in a hash database object."""
        return self.get(key, default, as_raw, int)

    def get_float(self, key, default=None, as_raw=False):
        """Retrieve a double precision record in a hash database
        object."""
        return self.get(key, default, as_raw, float)

    def vsiz(self, key, as_raw=False):
        """Get the size of the value of a Python object in a hash
        database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.hdb_vsiz(self.db, c_key, c_key_len)
        if result == -1:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def keys(self, as_type=None):
        """Get all the keys of a hash database object."""
        return list(self.iterkeys(as_type))

    def iterkeys(self, as_type=None):
        """Iterate for every key in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            c_key, c_key_len = tc.hdb_iternext(self.db)
            if not c_key:
                break
            key = util.deserialize(c_key, c_key_len, as_type)
            yield key

    def values(self, as_type=None):
        """Get all the values of a hash database object."""
        return list(self.itervalues(as_type))

    def itervalues(self, as_type=None):
        """Iterate for every value in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            c_key, c_key_len = tc.hdb_iternext(self.db)
            if not c_key:
                break
            (c_value, c_value_len) = tc.hdb_get(self.db, c_key, c_key_len)
            value = util.deserialize(c_value, c_value_len, as_type)
            yield value

    def items(self, key_type=None, value_type=None):
        """Get all the items of a hash database object."""
        return list(self.iteritems(key_type, value_type))

    def iteritems(self, key_type=None, value_type=None):
        """Iterate for every key / value in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            xstr_key = tc.tcxstrnew()
            xstr_value = tc.tcxstrnew()
            result = tc.hdb_iternext3(self.db, xstr_key, xstr_value)
            if not result:
                break
            key = util.deserialize_xstr(xstr_key, key_type)
            value = util.deserialize_xstr(xstr_value, value_type)
            yield (key, value)

    def fwmkeys(self, prefix, max_=-1, as_raw=True):
        """Get forward matching string keys in a hash database object."""
        (c_prefix, c_prefix_len) = util.serialize(prefix, as_raw)
        tclist_objs = tc.hdb_fwmkeys(self.db, c_prefix, c_prefix_len, max_)
        if not tclist_objs:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        as_type = util.get_type(prefix, as_raw)
        return util.deserialize_tclist(tclist_objs, as_type)

    def add_int(self, key, num, as_raw=False):
        """Add an integer to a record in a hash database object."""
        assert isinstance(num, int), 'Value is not an integer'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.hdb_addint(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def add_float(self, key, num, as_raw=False):
        """Add a real number to a record in a hash database object."""
        assert isinstance(num, float), 'Value is not a float'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.hdb_adddouble(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def foreach(self, proc, op, key_type=None, value_type=None):
        """Process each record atomically of a hash database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, key_type)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, value_type)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.hdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def has_key(self, key, raw_key=False):
        """Return True if hash database object has the key."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        return tc.hdb_iterinit2(self.db, c_key, c_key_len)
