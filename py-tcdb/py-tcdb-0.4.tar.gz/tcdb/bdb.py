# -*- coding: utf-8 -*-
# Tokyo Cabinet Python ctypes binding.

"""
BDB is an implementation of bsddb-like API for Tokyo Cabinet B+ tree
database.

We need to import 'bdb' class, and use it like that:

>>> from tcdb.bdb import BDB

>>> db = BDB()             # Create a new database object
>>> db.open('casket.tcb')  # By default create it if don't exist

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
FOPEN     = 1 << 0            # whether opened
FFATAL    = 1 << 1            # whether with fatal error

# enumeration for tuning options
TLARGE    = 1 << 0            # use 64-bit bucket array
TDEFLATE  = 1 << 1            # compress each page with Deflate
TBZIP     = 1 << 2            # compress each record with BZIP2
TTCBS     = 1 << 3            # compress each page with TCBS
TEXCODEC  = 1 << 4            # compress each record with outer functions

# enumeration for open modes
OREADER   = 1 << 0            # open as a reader
OWRITER   = 1 << 1            # open as a writer
OCREAT    = 1 << 2            # writer creating
OTRUNC    = 1 << 3            # writer truncating
ONOLCK    = 1 << 4            # open without locking
OLCKNB    = 1 << 5            # lock without blocking
OTSYNC    = 1 << 6            # synchronize every transaction

# enumeration for cursor put mode
CPCURRENT = 0                 # current
CPBEFORE  = 1                 # before
CPAFTER   = 2                 # after


class CursorSimple(object):
    def __init__(self, db):
        """Create a cursor from a B+ tree database object."""
        self.db = db
        self.cur = tc.bdb_curnew(db)

    def __del__(self):
        """Delete the cursor from a B+ tree database object."""
        if self.cur:
            self.close()

    def close(self):
        """Delete the cursor from a B+ tree database object."""
        tc.bdb_curdel(self.cur)
        self.cur = None

    def first(self):
        """Move a cursor object to the first record."""
        return tc.bdb_curfirst(self.cur)

    def last(self):
        """Move a cursor object to the last record."""
        return tc.bdb_curlast(self.cur)

    def jump(self, key):
        """Move a cursor object to the front of records corresponding
        a key."""
        result = tc.bdb_curjump2(self.cur, key)
        if not result:
            raise KeyError(key)
        return result

    def prev(self):
        """Move a cursor object to the previous record."""
        result = tc.bdb_curprev(self.cur)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def next(self):
        """Move a cursor object to the next record."""
        result = tc.bdb_curnext(self.cur)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def put(self, value, cpmode=CPCURRENT):
        """Insert a record around a cursor object."""
        result = tc.bdb_curput(self.cur, value, cpmode)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def key(self):
        """Get the key of the record where the cursor object is."""
        key = tc.bdb_curkey2(self.cur)
        if not key:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return key.value

    def value(self):
        """Get the value of the record where the cursor object is."""
        value = tc.bdb_curval2(self.cur)
        if not value:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return value.value

    def record(self):
        """Get the key and the value of the record where the cursor
        object is."""
        xstr_key = tc.tcxstrnew()
        xstr_value = tc.tcxstrnew()
        result = tc.bdb_currec(self.cur, xstr_key, xstr_value)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        key = util.deserialize_xstr(xstr_key, str)
        value = util.deserialize_xstr(xstr_value, str)
        return (key, value)

    def jumpback(self, key):
        """Move a cursor object to the rear of records corresponding a
        key string."""
        result = tc.bdb_curjumpback2(self.cur, key)
        if not result:
            raise KeyError(key)
        return result


class Cursor(CursorSimple):
    def __init__(self, db):
        """Create a cursor from a B+ tree database object."""
        CursorSimple.__init__(self, db)

    def jump(self, key, as_raw=False):
        """Move a cursor object to the front of records corresponding
        a key."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_curjump(self.cur, c_key, c_key_len)
        if not result:
            raise KeyError(key)
        return result

    def put(self, value, cpmode=CPCURRENT, as_raw=False):
        """Insert a record around a cursor object."""
        (c_value, c_value_len) = util.serialize(value, as_raw)
        result = tc.bdb_curput(self.cur, c_value, c_value_len, cpmode)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def put_str(self, value, cpmode=CPCURRENT):
        """Insert a string record around a cursor object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.put(value, cpmode, True)

    def put_unicode(self, value, cpmode=CPCURRENT):
        """Insert an unicode record around a cursor object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.put(value, cpmode, True)

    def put_int(self, value, cpmode=CPCURRENT):
        """Insert an integer record around a cursor object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.put(value, cpmode, True)

    def put_float(self, value, cpmode=CPCURRENT):
        """Insert a double precision record around a cursor object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.put(value, cpmode, True)

    def key(self, as_type=None):
        """Get the key of the record where the cursor object is."""
        c_key, c_key_len = tc.bdb_curkey(self.cur)
        if not c_key:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        key = util.deserialize(c_key, c_key_len, as_type)
        return key

    def value(self, as_type=None):
        """Get the value of the record where the cursor object is."""
        c_value, c_value_len = tc.bdb_curval(self.cur)
        if not c_value:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        value = util.deserialize(c_value, c_value_len, as_type)
        return value

    def value_str(self):
        """Get the value of a string record where the cursor object
        is."""
        return self.value(str)

    def value_unicode(self):
        """Get the value of an unicode string record where the cursor
        object is."""
        return self.value(unicode)

    def value_int(self):
        """Get the value of an integer record where the cursor object
        is."""
        return self.value(int)

    def value_float(self):
        """Get the value of a double precision record where the cursor
        object is."""
        return self.value(float)

    def record(self, key_type=None, value_type=None):
        """Get the key and the value of the record where the cursor
        object is."""
        xstr_key = tc.tcxstrnew()
        xstr_value = tc.tcxstrnew()
        result = tc.bdb_currec(self.cur, xstr_key, xstr_value)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        key = util.deserialize_xstr(xstr_key, key_type)
        value = util.deserialize_xstr(xstr_value, value_type)
        return (key, value)

    def jumpback(self, key, as_raw=False):
        """Move a cursor object to the rear of records corresponding a
        key."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_curjumpback(self.cur, c_key, c_key_len)
        if not result:
            raise KeyError(key)
        return result


class BDBSimple(object):
    def __init__(self):
        """Create a B+ tree database object."""
        self.db = tc.bdb_new()

    def __del__(self):
        """Delete a B+ tree database object."""
        tc.bdb_del(self.db)

    def setmutex(self):
        """Set mutual exclusion control of a B+ tree database object
        for threading."""
        return tc.bdb_setmutex(self.db)

    def setcmpfunc(self, cmp_, cmpop):
        """Set the custom comparison function of a B+ tree database
        object."""
        def cmp_wraper(c_keya, c_keya_len, c_keyb, c_keyb_len, op):
            keya = util.deserialize(ctypes.cast(c_keya, ctypes.c_void_p),
                                    c_keya_len, str)
            keyb = util.deserialize(ctypes.cast(c_keyb, ctypes.c_void_p),
                                    c_keyb_len, str)
            return cmp_(keya, keyb, ctypes.cast(op, ctypes.c_char_p).value)

        # If cmp_ is a string, it indicate a native tccmpxxx funcion.
        native = {
            None: tc.tccmplexical,
            'default': tc.tccmplexical,
            'tccmplexical': tc.tccmplexical,
            'tccmpdecimal': tc.tccmpdecimal,
            'tccmpint32': tc.tccmpint32,
            'tccmpint64': tc.tccmpint64
            }
        if cmp_ in native:
            result = tc.bdb_setcmpfunc(self.db, native[cmp_], cmpop)
        else:
            result = tc.bdb_setcmpfunc(self.db, tc.TCCMP(cmp_wraper), cmpop)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def tune(self, lmemb=0, nmemb=0, bnum=0, apow=-1, fpow=-1, opts=0):
        """Set the tuning parameters of a B+ tree database object."""
        result = tc.bdb_tune(self.db, lmemb, nmemb, bnum, apow, fpow, opts)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setcache(self, lcnum=0, ncnum=0):
        """Set the caching parameters of a B+ tree database object."""
        result = tc.bdb_setcache(self.db, lcnum, ncnum)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setxmsiz(self, xmsiz=0):
        """Set the size of the extra mapped memory of a B+ tree
        database object."""
        result = tc.bdb_setxmsiz(self.db, xmsiz)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setdfunit(self, dfunit=0):
        """Set the unit step number of auto defragmentation of a B+
        tree database object."""
        result = tc.bdb_setdfunit(self.db, dfunit)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def open(self, path, omode=OWRITER|OCREAT, lmemb=0, nmemb=0, bnum=0,
             apow=-1, fpow=-1, opts=0, lcnum=0, ncnum=0, xmsiz=0, dfunit=0):
        """Open a database file and connect a B+ tree database object."""
        if lmemb or nmemb or bnum or apow >= 0 or fpow >= 0 or opts:
            self.tune(lmemb, nmemb, bnum, apow, fpow, opts)
        if lcnum or ncnum:
            self.setcache(lcnum, ncnum)
        if xmsiz:
            self.setxmsiz(xmsiz)
        if dfunit:
            self.setdfunit(dfunit)

        if not tc.bdb_open(self.db, path, omode):
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))

    def close(self):
        """Close a B+ tree database object."""
        result = tc.bdb_close(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def __setitem__(self, key, value):
        """Store any Python object into a B+ tree database object."""
        return self.put(key, value)

    def put(self, key, value):
        """Store a string record into a B+ tree database object."""
        result = tc.bdb_put2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putkeep(self, key, value):
        """Store a new string record into a B+ tree database object."""
        return tc.bdb_putkeep2(self.db, key, value)

    def putcat(self, key, value):
        """Concatenate a string value at the end of the existing
        record in a B+ tree database object."""
        result = tc.bdb_putcat2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdup(self, key, value):
        """Store a string record into a B+ tree database object with
        allowing duplication of keys."""
        result = tc.bdb_putdup2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdup_iter(self, key, values):
        """Store records into a B+ tree database object with allowing
        duplication of keys."""
        (c_key, c_key_len) = util.serialize(key, str)
        tclist_vals = util.serialize_tclist(values, str)
        result = tc.bdb_putdup3(self.db, c_key, c_key_len, tclist_vals)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def __delitem__(self, key):
        """Remove a string record of a B+ tree database object."""
        return self.out(key)

    def out(self, key):
        """Remove a string record of a B+ tree database object."""
        result = tc.bdb_out2(self.db, key)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def outdup(self, key):
        """Remove records of a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, str)
        result = tc.bdb_out3(self.db, c_key, c_key_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def __getitem__(self, key):
        """Retrieve a Python object in a B+ tree database object."""
        return self._getitem(key)

    def _getitem(self, key):
        """Retrieve a Python object in a B+ tree database object."""
        value = tc.bdb_get2(self.db, key)
        if not value:
            raise KeyError(key)
        return value.value

    def get(self, key, default=None):
        """Retrieve a Python object in a B+ tree database object."""
        try:
            value = self._getitem(key)
        except KeyError:
            value = default
        return value

    def getdup(self, key, default=None):
        """Retrieve Python objects in a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, True)
        tclist_objs = tc.bdb_get4(self.db, c_key, c_key_len)
        if tclist_objs:
            value = util.deserialize_tclist(tclist_objs, str)
        else:
            value = default
        return value

    def vnum(self, key):
        """Get the number of records corresponding a key in a B+ tree
        database object."""
        result = tc.bdb_vnum2(self.db, key)
        if not result:
            raise KeyError(key)
        return result

    def vsiz(self, key):
        """Get the size of the value of a string record in a B+ tree
        database object."""
        result = tc.bdb_vsiz2(self.db, key)
        if result == -1:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def keys(self):
        """Get all the keys of a B+ tree database object."""
        return list(self.iterkeys())

    def iterkeys(self):
        """Iterate for every key in a B+ tree database object."""
        cursor = CursorSimple(self.db)
        if cursor.first():
            while True:
                key = cursor.key()
                yield key
                try:
                    cursor.next()
                except tc.TCException:
                    break
        cursor.close()

    def values(self):
        """Get all the values of a B+ tree database object."""
        return list(self.itervalues())

    def itervalues(self):
        """Iterate for every value in a B+ tree database object."""
        cursor = CursorSimple(self.db)
        if cursor.first():
            while True:
                value = cursor.value()
                yield value
                try:
                    cursor.next()
                except tc.TCException:
                    break
        cursor.close()

    def items(self):
        """Get all the items of a B+ tree database object."""
        return list(self.iteritems())

    def iteritems(self):
        """Iterate for every key / value in a B+ tree database object."""
        cursor = CursorSimple(self.db)
        if cursor.first():
            while True:
                key, value = cursor.record()
                yield (key, value)
                try:
                    cursor.next()
                except tc.TCException:
                    break
        cursor.close()

    def __iter__(self):
        """Iterate for every key in a B+ tree database object."""
        return self.iterkeys()

    def range(self, keya=None, inca=True, keyb=None, incb=True, max_=-1):
        """Get keys of ranged records in a B+ tree database object."""
        tclist_objs = tc.bdb_range2(self.db, keya, inca, keyb, incb, max_)
        if not tclist_objs:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return util.deserialize_tclist(tclist_objs, str)

    def fwmkeys(self, prefix, max_=-1):
        """Get forward matching string keys in a B+ tree database
        object."""
        tclist_objs = tc.bdb_fwmkeys2(self.db, prefix, max_)
        if not tclist_objs:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return util.deserialize_tclist(tclist_objs, str)

    def sync(self):
        """Synchronize updated contents of a B+ tree database object
        with the file and the device."""
        result = tc.bdb_sync(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def optimize(self, lmemb=None, nmemb=None, bnum=None, apow=None, fpow=None,
                 opts=None):
        """Optimize the file of a B+ tree database object."""
        kwargs = dict([x for x in (('lmemb', lmemb),
                                   ('nmemb', nmemb),
                                   ('bnum', bnum),
                                   ('apow', apow),
                                   ('fpow', fpow),
                                   ('opts', opts)) if x[1]])
        result = tc.bdb_optimize(self.db, **kwargs)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def vanish(self):
        """Remove all records of a B+ tree database object."""
        result = tc.bdb_vanish(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def copy(self, path):
        """Copy the database file of a B+ tree database object."""
        result = tc.bdb_copy(self.db, path)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def tranbegin(self):
        """Begin the transaction of a B+ tree database object."""
        result = tc.bdb_tranbegin(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def trancommit(self):
        """Commit the transaction of a B+ tree database object."""
        result = tc.bdb_trancommit(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def tranabort(self):
        """Abort the transaction of a B+ tree database object."""
        result = tc.bdb_tranabort(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
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
        """Get the file path of a B+ tree database object."""
        result = tc.bdb_path(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def __len__(self):
        """Get the number of records of a B+ tree database object."""
        return tc.bdb_rnum(self.db)

    def fsiz(self):
        """Get the size of the database file of a B+ tree database
        object."""
        result = tc.bdb_fsiz(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def setecode(self, ecode, filename, line, func):
        """Set the error code of a B+ tree database object."""
        tc.bdb_setecode(self.db, ecode, filename, line, func)

    def setdbgfd(self, fd):
        """Set the file descriptor for debugging output."""
        tc.bdb_setdbgfd(self.db, fd)

    def dbgfd(self):
        """Get the file descriptor for debugging output."""
        return tc.bdb_dbgfd(self.db)

    def hasmutex(self):
        """Check whether mutual exclusion control is set to a B+ tree
        database object."""
        return tc.bdb_hasmutex(self.db)

    def memsync(self, phys):
        """Synchronize updating contents on memory of a B+ tree
        database object."""
        result = tc.bdb_memsync(self.db, phys)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def cmpfunc(self):
        """Get the comparison function of a B+ tree database
        object."""
        return tc.bdb_cmpfunc(self.db)

    def cmpop(self):
        """Get the opaque object for the comparison function of a B+
        tree database object."""
        return tc.bdb_cmpop(self.db)

    def lmemb(self):
        """Get the maximum number of cached leaf nodes of a B+ tree
        database object."""
        return tc.bdb_lmemb(self.db)

    def lnum(self):
        """Get the number of the leaf nodes of B+ tree database
        object."""
        return tc.bdb_lnum(self.db)

    def nnum(self):
        """Get the number of the non-leaf nodes of B+ tree database
        object."""
        return tc.bdb_nnum(self.db)

    def bnum(self):
        """Get the number of elements of the bucket array of a B+ tree
        database object."""
        return tc.bdb_bnum(self.db)

    def align(self):
        """Get the record alignment of a B+ tree database object."""
        return tc.bdb_align(self.db)

    def fbpmax(self):
        """Get the maximum number of the free block pool of a B+ tree
        database object."""
        return tc.bdb_fbpmax(self.db)

    def inode(self):
        """Get the inode number of the database file of a B+ tree
        database object."""
        return tc.bdb_inode(self.db)

    def mtime(self):
        """Get the modification time of the database file of a B+ tree
        database object."""
        return datetime.datetime.fromtimestamp(tc.bdb_mtime(self.db))

    def flags(self):
        """Get the additional flags of a B+ tree database object."""
        return tc.bdb_flags(self.db)

    def opts(self):
        """Get the options of a B+ tree database object."""
        return tc.bdb_opts(self.db)

    def opaque(self):
        """Get the pointer to the opaque field of a B+ tree database
        object."""
        return tc.bdb_opaque(self.db)

    def bnumused(self):
        """Get the number of used elements of the bucket array of a B+
        tree database object."""
        return tc.bdb_bnumused(self.db)

    def setlsmax(self, lsmax):
        """Set the maximum size of each leaf node."""
        result = tc.bdb_setlsmax(self.db, lsmax)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def setcapnum(self, capnum):
        """Set the capacity number of records."""
        result = tc.bdb_setcapnum(self.db, capnum)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    # def setcodecfunc(self, enc, encop, dec, decop):
    #     """Set the custom codec functions of a B+ tree database
    #     object."""
    #     result = tc.bdb_setcodecfunc(self.db, TCCODEC(enc), encop,
    #                                  TCCODEC(dec), decop)
    #     if not result:
    #         raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
    #     return result

    def dfunit(self):
        """Get the unit step number of auto defragmentation of a B+
        tree database object."""
        return tc.bdb_dfunit(self.db)

    def defrag(self, step):
        """Perform dynamic defragmentation of a B+ tree database
        object."""
        result = tc.bdb_defrag(self.db, step)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def cacheclear(self):
        """Clear the cache of a B+ tree database object."""
        result = tc.bdb_cacheclear(self.db)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdupback(self, key, value):
        """Store a new string record into a B+ tree database object
        with backward duplication."""
        result = tc.bdb_putdupback2(self.db, key, value)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    # def putproc(self, key, value, proc, op):
    #     """Store a record into a B+ tree database object with a
    #     duplication handler."""
    #     # See tc.bdb_putproc

    def foreach(self, proc, op):
        """Process each record atomically of a B+ tree database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, str)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, str)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.bdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def __contains__(self, key):
        """Return True if B+ tree database object has the key."""
        return self.has_key(key)

    def has_key(self, key):
        """Return True if B+ tree database object has the key."""
        cursor = CursorSimple(self.db)
        result = False
        try:
            cursor.jump(key)
        except KeyError:
            pass
        else:
            if cursor.key() == key:
                result = True
        finally:
            cursor.close()
        return result

    def cursor(self):
        """Create a cursor object associated with the B+ tree database
        object."""
        return CursorSimple(self.db)


class BDB(BDBSimple):
    def __init__(self):
        """Create a B+ tree database object."""
        BDBSimple.__init__(self)

    def setcmpfunc(self, cmp_, cmpop, raw_key=False, value_type=None):
        """Set the custom comparison function of a B+ tree database
        object."""
        def cmp_wraper(c_keya, c_keya_len, c_keyb, c_keyb_len, op):
            keya = util.deserialize(ctypes.cast(c_keya, ctypes.c_void_p),
                                    c_keya_len, raw_key)
            keyb = util.deserialize(ctypes.cast(c_keyb, ctypes.c_void_p),
                                    c_keyb_len, value_type)
            return cmp_(keya, keyb, ctypes.cast(op, ctypes.c_char_p).value)

        # If cmp_ is a string, it indicate a native tccmpxxx funcion.
        native = {
            None: tc.tccmplexical,
            'default': tc.tccmplexical,
            'tccmplexical': tc.tccmplexical,
            'tccmpdecimal': tc.tccmpdecimal,
            'tccmpint32': tc.tccmpint32,
            'tccmpint64': tc.tccmpint64
            }
        if cmp_ in native:
            result = tc.bdb_setcmpfunc(self.db, native[cmp_], cmpop)
        else:
            result = tc.bdb_setcmpfunc(self.db, tc.TCCMP(cmp_wraper), cmpop)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def put(self, key, value, raw_key=False, raw_value=False):
        """Store any Python object into a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.bdb_put(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def put_str(self, key, value, as_raw=False):
        """Store a string record into a B+ tree database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.put(key, value, as_raw, True)

    def put_unicode(self, key, value, as_raw=False):
        """Store an unicode string record into a B+ tree database
        object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.put(key, value, as_raw, True)

    def put_int(self, key, value, as_raw=False):
        """Store an integer record into a B+ tree database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.put(key, value, as_raw, True)

    def put_float(self, key, value, as_raw=False):
        """Store a double precision record into a B+ tree database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.put(key, value, as_raw, True)

    def putkeep(self, key, value, raw_key=False, raw_value=False):
        """Store a new Python object into a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        return tc.bdb_putkeep(self.db, c_key, c_key_len, c_value, c_value_len)

    def putkeep_str(self, key, value, as_raw=False):
        """Store a new string record into a B+ tree database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_unicode(self, key, value, as_raw=False):
        """Store a new unicode string record into a B+ tree database
        object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_int(self, key, value, as_raw=False):
        """Store a new integer record into a B+ tree database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_float(self, key, value, as_raw=False):
        """Store a new double precision record into a B+ tree database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putkeep(key, value, as_raw, True)

    def putcat(self, key, value, raw_key=False, raw_value=False):
        """Concatenate an object value at the end of the existing
        record in a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.bdb_putcat(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putcat_str(self, key, value, as_raw=False):
        """Concatenate a string value at the end of the existing
        record in a B+ tree database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putcat(key, value, as_raw, True)

    def putcat_unicode(self, key, value, as_raw=False):
        """Concatenate an unicode string value at the end of the
        existing record in a B+ tree database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putcat(key, value, as_raw, True)

    def putdup(self, key, value, raw_key=False, raw_value=False):
        """Store a Python object into a B+ tree database object with
        allowing duplication of keys."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.bdb_putdup(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdup_str(self, key, value, as_raw=False):
        """Store a string record into a B+ tree database object with
        allowing duplication of keys."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putdup(key, value, as_raw, True)

    def putdup_unicode(self, key, value, as_raw=False):
        """Store an unicode string record into a B+ tree database
        object with allowing duplication of keys."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putdup(key, value, as_raw, True)

    def putdup_int(self, key, value, as_raw=False):
        """Store an integer record into a B+ tree database object with
        allowing duplication of keys."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putdup(key, value, as_raw, True)

    def putdup_float(self, key, value, as_raw=False):
        """Store a double precision record into a B+ tree database
        object with allowing duplication of keys."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putdup(key, value, as_raw, True)

    def putdup_iter(self, key, values, raw_key=False, raw_value=False):
        """Store Python records into a B+ tree database object with
        allowing duplication of keys."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        tclist_vals = util.serialize_tclist(values, raw_value)
        result = tc.bdb_putdup3(self.db, c_key, c_key_len, tclist_vals)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdup_iter_str(self, key, values, as_raw=False):
        """Store string records into a B+ tree database object with
        allowing duplication of keys."""
        assert all([isinstance(v, str) for v in values]), \
            'Value is not a string'
        return self.putdup_iter(key, values, as_raw, True)

    def putdup_iter_unicode(self, key, values, as_raw=False):
        """Store unicode string records into a B+ tree database object
        with allowing duplication of keys."""
        assert all([isinstance(v, unicode) for v in values]), \
            'Value is not an unicode string'
        return self.putdup_iter(key, values, as_raw, True)

    def putdup_iter_int(self, key, values, as_raw=False):
        """Store integer records into a B+ tree database object with
        allowing duplication of keys."""
        assert all([isinstance(v, int) for v in values]), \
            'Value is not an integer'
        return self.putdup_iter(key, values, as_raw, True)

    def putdup_iter_float(self, key, values, as_raw=False):
        """Store double precision records into a B+ tree database
        object with allowing duplication of keys."""
        assert all([isinstance(v, float) for v in values]), \
            'Value is not a float'
        return self.putdup_iter(key, values, as_raw, True)

    def out(self, key, as_raw=False):
        """Remove a Python object of a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_out(self.db, c_key, c_key_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def outdup(self, key, as_raw=False):
        """Remove Python objects of a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_out3(self.db, c_key, c_key_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def _getitem(self, key, raw_key=False, value_type=None):
        """Retrieve a Python object in a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = tc.bdb_get(self.db, c_key, c_key_len)
        if not c_value:
            raise KeyError(key)
        return util.deserialize(c_value, c_value_len, value_type)

    def get(self, key, default=None, raw_key=False, value_type=None):
        """Retrieve a Python object in a B+ tree database object."""
        try:
            value = self._getitem(key, raw_key, value_type)
        except KeyError:
            value = default
        return value

    def get_str(self, key, default=None, as_raw=False):
        """Retrieve a string record in a B+ tree database object."""
        return self.get(key, default, as_raw, str)

    def get_unicode(self, key, default=None, as_raw=False):
        """Retrieve an unicode string record in a B+ tree database
        object."""
        return self.get(key, default, as_raw, unicode)

    def get_int(self, key, default=None, as_raw=False):
        """Retrieve an integer record in a B+ tree database object."""
        return self.get(key, default, as_raw, int)

    def get_float(self, key, default=None, as_raw=False):
        """Retrieve a double precision record in a B+ tree database
        object."""
        return self.get(key, default, as_raw, float)

    def _getdup(self, key, raw_key=False, value_type=None):
        """Retrieve Python objects in a B+ tree database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        tclist_objs = tc.bdb_get4(self.db, c_key, c_key_len)
        if not tclist_objs:
            raise KeyError(key)
        return util.deserialize_tclist(tclist_objs, value_type)

    def getdup(self, key, default=None, raw_key=False, value_type=None):
        """Retrieve Python objects in a B+ tree database object."""
        try:
            value = self._getdup(key, raw_key, value_type)
        except KeyError:
            value = default
        return value

    def getdup_str(self, key, default=None, as_raw=False):
        """Retrieve a string record in a B+ tree database object."""
        return self.getdup(key, default, as_raw, str)

    def getdup_unicode(self, key, default=None, as_raw=False):
        """Retrieve an unicode string record in a B+ tree database
        object."""
        return self.getdup(key, default, as_raw, unicode)

    def getdup_int(self, key, default=None, as_raw=False):
        """Retrieve an integer record in a B+ tree database object."""
        return self.getdup(key, default, as_raw, int)

    def getdup_float(self, key, default=None, as_raw=False):
        """Retrieve a double precision record in a B+ tree database
        object."""
        return self.getdup(key, default, as_raw, float)

    def vnum(self, key, as_raw=False):
        """Get the number of records corresponding a key in a B+ tree
        database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_vnum(self.db, c_key, c_key_len)
        if not result:
            raise KeyError(key)
        return result

    def vsiz(self, key, as_raw=False):
        """Get the size of the value of a record in a B+ tree database
        object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_vsiz(self.db, c_key, c_key_len)
        if result == -1:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def keys(self, as_type=None):
        """Get all the keys of a B+ tree database object."""
        return list(self.iterkeys(as_type))

    def iterkeys(self, as_type=None):
        """Iterate for every key in a B+ tree database object."""
        cursor = Cursor(self.db)
        if cursor.first():
            while True:
                key = cursor.key(as_type)
                yield key
                try:
                    cursor.next()
                except tc.TCException:
                    break
        cursor.close()

    def values(self, as_type=None):
        """Get all the values of a B+ tree database object."""
        return list(self.itervalues(as_type))

    def itervalues(self, as_type=None):
        """Iterate for every value in a B+ tree database object."""
        cursor = Cursor(self.db)
        if cursor.first():
            while True:
                value = cursor.value(as_type)
                yield value
                try:
                    cursor.next()
                except tc.TCException:
                    break
        cursor.close()

    def items(self, key_type=None, value_type=None):
        """Get all the items of a B+ tree database object."""
        return list(self.iteritems(key_type, value_type))

    def iteritems(self, key_type=None, value_type=None):
        """Iterate for every key / value in a B+ tree database object."""
        cursor = Cursor(self.db)
        if cursor.first():
            while True:
                key, value = cursor.record(key_type, value_type)
                yield (key, value)
                try:
                    cursor.next()
                except tc.TCException:
                    break
        cursor.close()

    def range(self, keya=None, inca=True, keyb=None, incb=True, max_=-1,
              as_raw=True):
        """Get keys of ranged records in a B+ tree database object."""
        (c_keya, c_keya_len) = util.serialize(keya, as_raw)
        (c_keyb, c_keyb_len) = util.serialize(keyb, as_raw)
        tclist_objs = tc.bdb_range(self.db, c_keya, c_keya_len, inca,
                                   c_keyb, c_keyb_len, incb, max_)
        if not tclist_objs:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        as_type = util.get_type(keya, as_raw)
        return util.deserialize_tclist(tclist_objs, as_type)

    def fwmkeys(self, prefix, max_=-1, as_raw=True):
        """Get forward matching string keys in a B+ tree database
        object."""
        (c_prefix, c_prefix_len) = util.serialize(prefix, as_raw)
        tclist_objs = tc.bdb_fwmkeys(self.db, c_prefix, c_prefix_len, max_)
        if not tclist_objs:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        as_type = util.get_type(prefix, as_raw)
        return util.deserialize_tclist(tclist_objs, as_type)

    def add_int(self, key, num, as_raw=False):
        """Add an integer to a record in a B+ tree database object."""
        assert isinstance(num, int), 'Value is not an integer'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_addint(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def add_float(self, key, num, as_raw=False):
        """Add a real number to a record in a B+ tree database object."""
        assert isinstance(num, float), 'Value is not a float'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.bdb_adddouble(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdupback(self, key, value, raw_key=False, raw_value=False):
        """Store a new Python object into a B+ tree database object
        with backward duplication."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.bdb_putdupback(self.db, c_key, c_key_len, c_value,
                                   c_value_len)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def putdupback_str(self, key, value, as_raw=False):
        """Store a string record into a B+ tree database object with
        allowing duplication of keys."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putdupback(key, value, as_raw, True)

    def putdupback_unicode(self, key, value, as_raw=False):
        """Store an unicode string record into a B+ tree database
        object with backward duplication."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putdupback(key, value, as_raw, True)

    def putdupback_int(self, key, value, as_raw=False):
        """Store an integer record into a B+ tree database object with
        backward duplication."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putdupback(key, value, as_raw, True)

    def putdupback_float(self, key, value, as_raw=False):
        """Store a double precision record into a B+ tree database
        object with backward duplication."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putdupback(key, value, as_raw, True)

    def foreach(self, proc, op, key_type=None, value_type=None):
        """Process each record atomically of a B+ tree database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, key_type)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, value_type)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.bdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.bdb_errmsg(tc.bdb_ecode(self.db)))
        return result

    def has_key(self, key, raw_key=False):
        """Return True if B+ tree database object has the key."""
        cursor = Cursor(self.db)
        result = False
        try:
            cursor.jump(key, raw_key)
        except KeyError:
            pass
        else:
            if cursor.key(util.get_type(key, raw_key)) == key:
                result = True
        finally:
            cursor.close()
        return result

    def cursor(self):
        """Create a cursor object associated with the B+ tree database
        object."""
        return Cursor(self.db)
