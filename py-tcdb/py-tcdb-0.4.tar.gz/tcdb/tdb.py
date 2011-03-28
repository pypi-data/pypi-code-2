# -*- coding: utf-8 -*-
# Tokyo Cabinet Python ctypes binding.

"""
TDB is an implementation of bsddb-like API for Tokyo Cabinet table
database.

We need to import 'TDB' class, and use it like that:

>>> from tcdb.tdb import TDB

>>> db = TDB()             # Create a new database object
>>> db.open('casket.tct')  # By default create it if don't exist

>>> db.put("foo", {"hop": 10, "boo": "boo value"})
True

>>> db.get("foo")["hop"]
10

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
TDEFLATE  = 1 << 1            # compress each record with Deflate
TBZIP     = 1 << 2            # compress each record with BZIP2
TTCBS     = 1 << 3            # compress each record with TCBS
TEXCODEC  = 1 << 4            # compress each record with custom functions

# enumeration for open modes
OREADER   = 1 << 0            # open as a reader
OWRITER   = 1 << 1            # open as a writer
OCREAT    = 1 << 2            # writer creating
OTRUNC    = 1 << 3            # writer truncating
ONOLCK    = 1 << 4            # open without locking
OLCKNB    = 1 << 5            # lock without blocking
OTSYNC    = 1 << 6            # synchronize every transaction

# enumeration for index types 
ITLEXICAL = 0                 # lexical string
ITDECIMAL = 1                 # decimal string
ITTOKEN   = 2                 # token inverted index
ITQGRAM   = 3                 # q-gram inverted index
ITOPT     = 9998,             # optimize
ITVOID    = 9999,             # void
ITKEEP    = 1 << 24           # keep existing index

# enumeration for query conditions
QCSTREQ   = 0                 # string is equal to
QCSTRINC  = 1                 # string is included in
QCSTRBW   = 2                 # string begins with
QCSTREW   = 3                 # string ends with
QCSTRAND  = 4                 # string includes all tokens in
QCSTROR   = 5                 # string includes at least one token in
QCSTROREQ = 6                 # string is equal to at least one token in
QCSTRRX   = 7                 # string matches regular expressions of
QCNUMEQ   = 8                 # number is equal to
QCNUMGT   = 9                 # number is greater than
QCNUMGE   = 10                # number is greater than or equal to
QCNUMLT   = 11                # number is less than
QCNUMLE   = 12                # number is less than or equal to
QCNUMBT   = 13                # number is between two tokens of
QCNUMOREQ = 14                # number is equal to at least one token in
QCFTSPH   = 15                # full-text search with the phrase of
QCFTSAND  = 16                # full-text search with all tokens in
QCFTSOR   = 17                # full-text search with at least one token in
QCFTSEX   = 18                # full-text search with the compound expression of
QCNEGATE  = 1 << 24           # negation flag
QCNOIDX   = 1 << 25           # no index flag

# enumeration for order types
QOSTRASC  = 0                 # string ascending
QOSTRDESC = 1                 # string descending
QONUMASC  = 2                 # number ascending
QONUMDESC = 3                 # number descending

# enumeration for set operation types
MSUNION   = 0                 # union
MSISECT   = 1                 # intersection
MSDIFF    = 2                 # difference

# enumeration for post treatments
QPPUT     = 1 << 0            # modify the record
QPOUT     = 1 << 1            # remove the record
QPSTOP    = 1 << 24           # stop the iteration


class Query(object):
    def __init__(self, db):
        """Create a query object."""
        self.db = db
        self.qry = tc.tdb_qrynew(db)

    def __del__(self):
        """Delete a query object."""
        if self.qry:
            self.close()

    def close(self):
        """Delete a query object."""
        tc.tdb_qrydel(self.qry)
        self.qry = None

    def addcond(self, name, op, expr):
        """Add a narrowing condition to a query object."""
        tc.tdb_qryaddcond(self.qry, name, op, expr)

    def setorder(self, name, type_):
        """Set the order of a query object."""
        tc.tdb_qrysetorder(self.qry, name, type_)

    def setlimit(self, max_=-1, skip=0):
        """Set the limit number of records of the result of a query
        object."""
        tc.tdb_qrysetlimit(self.qry, max_, skip)

    def search(self, as_type=None):
        """Execute the search of a query object."""
        tclist_pkeys = tc.tdb_qrysearch(self.qry)
        pkeys = util.deserialize_tclist(tclist_pkeys, as_type=as_type)
        return pkeys

    def searchout(self):
        """Remove each record corresponding to a query object."""
        result = tc.tdb_qrysearchout(self.qry)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def searchout_non_atomic(self):
        """Remove each record corresponding to a query object with
        non-atomic fashion."""
        result = tc.tdb_qrysearchout2(self.qry)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def proc(self, proc, op):
        """Process each record corresponding to a query object."""
        def proc_wraper(c_pkey, c_pkey_len, c_cols, op):
            pkey = util.deserialize(ctypes.cast(c_pkey, ctypes.c_void_p),
                                    c_pkey_len, as_type=int)
            cols = util.deserialize_tcmap(c_cols)
            return proc(pkey, cols, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.tdb_qryproc(self.qry, tc.TDBQRYPROC(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def proc_non_atomic(self, proc, op):
        """Process each record corresponding to a query object with
        non-atomic fashion."""
        def proc_wraper(c_pkey, c_pkey_len, c_cols, op):
            pkey = util.deserialize(ctypes.cast(c_pkey, ctypes.c_void_p),
                                    c_pkey_len, as_type=int)
            cols = util.deserialize_tcmap(c_cols)
            return proc(pkey, cols, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.tdb_qryproc2(self.qry, tc.TDBQRYPROC(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def hint(self):
        """Get the hint string of a query object."""
        return tc.tdb_qryhint(self.qry)

    def count(self):
        """Get the count of corresponding records of a query
        object."""
        return tc.tdb_qrycount(self.qry)

    @staticmethod
    def metasearch(qrys, type_, as_type=None):
        """Retrieve records with multiple query objects and get the
        set of the result."""
        qrys = [q.qry for q in qrys]
        tclist_pkeys = tc.tdb_metasearch(qrys, len(qrys), type_)
        pkeys = util.deserialize_tclist(tclist_pkeys, as_type=as_type)
        return pkeys
        

class TDB(object):
    def __init__(self):
        """Create a table database object."""
        self.db = tc.tdb_new()

    def __del__(self):
        """Delete a table database object."""
        tc.tdb_del(self.db)

    def setmutex(self):
        """Set mutual exclusion control of a table database object for
        threading."""
        return tc.tdb_setmutex(self.db)

    def tune(self, bnum=0, apow=-1, fpow=-1, opts=0):
        """Set the tuning parameters of a table database object."""
        result = tc.tdb_tune(self.db, bnum, apow, fpow, opts)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setcache(self, rcnum=0, lcnum=0, ncnum=0):
        """Set the caching parameters of a table database object."""
        result = tc.tdb_setcache(self.db, rcnum)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setxmsiz(self, xmsiz=0):
        """Set the size of the extra mapped memory of a table database
        object."""
        result = tc.tdb_setxmsiz(self.db, xmsiz)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setdfunit(self, dfunit=0):
        """Set the unit step number of auto defragmentation of a table
        database object."""
        result = tc.tdb_setdfunit(self.db, dfunit)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def open(self, path, omode=OWRITER|OCREAT, bnum=0, apow=-1, fpow=-1,
             opts=0, rcnum=0, lcnum=0, ncnum=0, xmsiz=0, dfunit=0):
        """Open a database file and connect a table database object."""
        self.setcache(rcnum, lcnum, ncnum)
        self.setxmsiz(xmsiz)
        self.setdfunit(dfunit)
        self.tune(bnum, apow, fpow, opts)

        if not tc.tdb_open(self.db, path, omode):
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))

    def close(self):
        """Close a table database object."""
        result = tc.tdb_close(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def __setitem__(self, key, value):
        """Store any Python object into a table database object."""
        return self.put(key, value)

    def put(self, key, cols, raw_key=False, raw_cols=False):
        """Store a record into a table database object."""
        assert isinstance(cols, dict)
        (c_key, c_key_len) = util.serialize(key, raw_key)
        cols_tcmap = util.serialize_tcmap(cols, raw_cols)
        result = tc.tdb_put(self.db, c_key, c_key_len, cols_tcmap)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def putkeep(self, key, cols, raw_key=False, raw_cols=False):
        """Store a new record into a table database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        cols_tcmap = util.serialize_tcmap(cols, raw_cols)
        return tc.tdb_putkeep(self.db, c_key, c_key_len, cols_tcmap)

    def putcat(self, key, cols, raw_key=False, raw_cols=False):
        """Concatenate columns of the existing record in a table
        database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        cols_tcmap = util.serialize_tcmap(cols, raw_cols)
        result = tc.tdb_putcat(self.db, c_key, c_key_len, cols_tcmap)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def __delitem__(self, key):
        """Remove a record of a table database object."""
        return self.out(key)

    def out(self, key, as_raw=False):
        """Remove a record of a table database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.tdb_out(self.db, c_key, c_key_len)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def __getitem__(self, key):
        """"Retrieve a record in a table database object."""
        return self._getitem(key)

    def _getitem(self, key, raw_key=False, schema=None):
        """"Retrieve a record in a table database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        cols_tcmap = tc.tdb_get(self.db, c_key, c_key_len)
        if not cols_tcmap:
            raise KeyError(key)
        return util.deserialize_tcmap(cols_tcmap, schema)

    def get(self, key, default=None, raw_key=False, schema=None):
        """"Retrieve a record in a table database object."""
        try:
            value = self._getitem(key, raw_key, schema)
        except KeyError:
            value = default
        return value

    def get_col(self, key, col, default=None, raw_key=False, value_type=None):
        """Retrieve the value of a column of a record in a table
        database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_col, c_col_len) = util.serialize(col, as_raw=True)
        (c_value, c_value_len) = tc.tdb_get4(self.db, c_key, c_key_len, c_col,
                                             c_col_len)
        if c_value:
            value = util.deserialize(c_value, c_value_len, value_type)
        else:
            value = default
        return value

    def get_col_str(self, key, col, default=None, raw_key=False):
        """Retrieve a string column of a record in a table database
        object."""
        return self.get_col(key, col, default, raw_key, str)

    def get_col_unicode(self, key, col, default=None, raw_key=False):
        """Retrieve an unicode string column of a record in a table
        database object."""
        return self.get_col(key, col, default, raw_key, unicode)

    def get_col_int(self, key, col, default=None, raw_key=False):
        """Retrieve an integer column of a record in a table database
        object."""
        return self.get_col(key, col, default, raw_key, int)

    def get_col_float(self, key, col, default=None, raw_key=False):
        """Retrieve a double precision column of a record in a table
        database object."""
        return self.get_col(key, col, default, raw_key, float)

    def vsiz(self, key, as_raw=False):
        """Get the size of the value of a Python object in a table
        database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.tdb_vsiz(self.db, c_key, c_key_len)
        if result == -1:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def keys(self, as_type=None):
        """Get all the keys of a table database object."""
        return list(self.iterkeys(as_type))

    def iterkeys(self, as_type=None):
        """Iterate for every key in a table database object."""
        if not tc.tdb_iterinit(self.db):
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        while True:
            c_key, c_key_len = tc.tdb_iternext(self.db)
            if not c_key:
                break
            key = util.deserialize(c_key, c_key_len, as_type)
            yield key

    def values(self, schema=None):
        """Get all the values of a table database object."""
        return list(self.itervalues(schema))

    def itervalues(self, schema=None):
        """Iterate for every value in a table database object."""
        if not tc.tdb_iterinit(self.db):
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        while True:
            cols_tcmap = tc.tdb_iternext3(self.db)
            if not cols_tcmap:
                break
            cols = util.deserialize_tcmap(cols_tcmap, schema)
            yield cols

    def items(self, key_type=None, schema=None):
        """Get all the items of a table database object."""
        return list(self.iteritems(key_type, schema))

    def iteritems(self, key_type=None, schema=None):
        """Iterate for every key / value in a table database object."""
        if not tc.tdb_iterinit(self.db):
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        while True:
            c_key, c_key_len = tc.tdb_iternext(self.db)
            if not c_key:
                break
            cols_tcmap = tc.tdb_get(self.db, c_key, c_key_len)
            key = util.deserialize(c_key, c_key_len, key_type)
            cols = util.deserialize_tcmap(cols_tcmap, schema)
            yield (key, cols)

    def __iter__(self):
        """Iterate for every key in a table database object."""
        return self.iterkeys()

    def fwmkeys(self, prefix, as_raw=True):
        """Get forward matching primary keys in a table database
        object."""
        (c_prefix, c_prefix_len) = util.serialize(prefix, as_raw)
        tclist_objs = tc.tdb_fwmkeys(self.db, c_prefix, c_prefix_len)
        if not tclist_objs:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        as_type = util.get_type(prefix, as_raw)
        return util.deserialize_tclist(tclist_objs, as_type)

    def add_int(self, key, num, as_raw=False):
        """Add an integer to a column of a record in a table database
        object."""
        assert isinstance(num, int), 'Value is not an integer'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.tdb_addint(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def add_float(self, key, num, as_raw=False):
        """Add a real number to a column of a record in a table
        database object."""
        assert isinstance(num, float), 'Value is not a float'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.tdb_adddouble(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def sync(self):
        """Synchronize updated contents of a table database object with
        the file and the device."""
        result = tc.tdb_sync(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def optimize(self, bnum=None, apow=None, fpow=None, opts=None):
        """Optimize the file of a table database object."""
        kwargs = dict([x for x in (('bnum', bnum),
                                   ('apow', apow),
                                   ('fpow', fpow),
                                   ('opts', opts)) if x[1]])
        result = tc.tdb_optimize(self.db, **kwargs)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def vanish(self):
        """Remove all records of a table database object."""
        result = tc.tdb_vanish(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def copy(self, path):
        """Copy the database file of a table database object."""
        result = tc.tdb_copy(self.db, path)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def tranbegin(self):
        """Begin the transaction of a table database object."""
        result = tc.tdb_tranbegin(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def trancommit(self):
        """Commit the transaction of a table database object."""
        result = tc.tdb_trancommit(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def tranabort(self):
        """Abort the transaction of a table database object."""
        result = tc.tdb_tranabort(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
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
        """Get the file path of a table database object."""
        result = tc.tdb_path(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def __len__(self):
        """Get the number of records of a table database object."""
        return tc.tdb_rnum(self.db)

    def fsiz(self):
        """Get the size of the database file of a table database
        object."""
        result = tc.tdb_fsiz(self.db)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setindex(self, name, type_):
        """Set a column index to a table database object."""
        result = tc.tdb_setindex(self.db, name, type_)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def genuid(self):
        """Generate a unique ID number of a table database object."""
        result = tc.tdb_genuid(self.db)
        if result == -1:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setecode(self, ecode, filename, line, func):
        """Set the error code of a table database object."""
        tc.tdb_setecode(self.db, ecode, filename, line, func)

    def setdbgfd(self, fd):
        """Set the file descriptor for debugging output."""
        tc.tdb_setdbgfd(self.db, fd)

    def dbgfd(self):
        """Get the file descriptor for debugging output."""
        return tc.tdb_dbgfd(self.db)

    def hasmutex(self):
        """Check whether mutual exclusion control is set to a table
        database object."""
        return tc.tdb_hasmutex(self.db)

    def memsync(self, phys):
        """Synchronize updating contents on memory of a table database
        object."""
        result = tc.tdb_memsync(self.db, phys)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def bnum(self):
        """Get the number of elements of the bucket array of a table
        database object."""
        return tc.tdb_bnum(self.db)

    def align(self):
        """Get the record alignment of a table database object."""
        return tc.tdb_align(self.db)

    def fbpmax(self):
        """Get the maximum number of the free block pool of a a table
        database object."""
        return tc.tdb_fbpmax(self.db)

    def inode(self):
        """Get the inode number of the database file of a table
        database object."""
        return tc.tdb_inode(self.db)

    def mtime(self):
        """Get the modification time of the database file of a table
        database object."""
        return datetime.datetime.fromtimestamp(tc.tdb_mtime(self.db))

    def flags(self):
        """Get the additional flags of a table database object."""
        return tc.tdb_flags(self.db)

    def opts(self):
        """Get the options of a table database object."""
        return tc.tdb_opts(self.db)

    def opaque(self):
        """Get the pointer to the opaque field of a table database
        object."""
        return tc.tdb_opaque(self.db)

    def bnumused(self):
        """Get the number of used elements of the bucket array of a
        table database object."""
        return tc.tdb_bnumused(self.db)

    def inum(self):
        """Get the number of column indices of a table database
        object."""
        return tc.tdb_inum(self.db)

    def uidseed(self):
        """Get the seed of unique ID unumbers of a table database
        object."""
        return tc.tdb_uidseed(self.db)

    def setuidseed(self, seed):
        """Set the seed of unique ID unumbers of a table database
        object."""
        result = tc.tdb_setuidseed(self.db, seed)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def setinvcache(self, iccmax, iccsync):
        """Set the parameters of the inverted cache of a table
        database object."""
        result = tc.tdb_setinvcache(self.db, iccmax, iccsync)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    # def setcodecfunc(self, enc, encop, dec, decop):
    #     """Set the custom codec functions of a table database
    #     object."""
    #     result = tc.tdb_setcodecfunc(self.db, TCCODEC(enc), encop,
    #                                  TCCODEC(dec), decop)
    #     if not result:
    #         raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
    #     return result

    def dfunit(self):
        """Get the unit step number of auto defragmentation of a table
        database object."""
        return tc.tdb_dfunit(self.db)

    def defrag(self, step):
        """Perform dynamic defragmentation of a table database
        object."""
        result = tc.tdb_defrag(self.db, step)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    # def cacheclear(self):
    #     """Clear the cache of a table tree database object."""
    #     result = tc.tdb_cacheclear(self.db)
    #     if not result:
    #         raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
    #     return result

    # def putproc(self, key, value, proc, op):
    #     """Store a record into a table database object with a
    #     duplication handler."""
    #     # See tc.tdb_putproc

    def foreach(self, proc, op, key_type=None, schema=None):
        """Process each record atomically of a table database
        object."""
        def proc_wraper(c_key, c_key_len, c_cols, c_cols_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, key_type)
            cols = util.deserialize(ctypes.cast(c_cols, ctypes.c_void_p),
                                    c_cols_len, str)
            return proc(key, cols, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.tdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def strtoindextype(self, str_):
        """Convert a string into the index type number."""
        result = tc.tdb_strtoindextype(str_)
        if result == -1:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def strtometasearchtype(self, str_):
        """Convert a string into the meta search type number."""
        result = tc.tdb_strtometasearchtype(str_)
        if result == -1:
            raise tc.TCException(tc.tdb_errmsg(tc.tdb_ecode(self.db)))
        return result

    def __contains__(self, key):
        """Return True if table database object has the key."""
        return self.has_key(key)

    def has_key(self, key, raw_key=False):
        """Return True if table database object has the key."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        return tc.tdb_iterinit2(self.db, c_key, c_key_len)

    def query(self):
        """Return a Query object associated with the table database
        object."""
        return Query(self.db)
