# -*- coding: utf-8 -*-
# Tokyo Cabinet Python ctypes binding.

"""
ADB is an implementation of bsddb-like API for Tokyo Cabinet abstract
database.

We need to import 'ADB' class, and use it like that:

>>> from tcdb.adb import ADB

>>> db = ADB()             # Create a new database object
>>> db.open('casket.ach')  # By default create it if don't exist

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

import tc
import util


# enumeration for open modes
OVOID = 0                     # not opened
OMDB  = 1                     # on-memory hash database
ONDB  = 2                     # on-memory tree database
OHDB  = 3                     # hash database
OBDB  = 4                     # B+ tree database
OFDB  = 5                     # fixed-length database
OTDB  = 6                     # table database
OSKEL = 7                     # skeleton database


class ADBSimple(object):
    def __init__(self):
        """Create an abstract database object."""
        self.db = tc.adb_new()

    def __del__(self):
        """Delete an abstract database object."""
        tc.adb_del(self.db)

    def open(self, name):
        """Open an abstract database."""
        if not tc.adb_open(self.db, name):
            self._raise('Error opening abstract database [%s]'%name)

    def close(self):
        """Close an abstract database object."""
        result = tc.adb_close(self.db)
        if not result:
            self._raise('Error closing abstract database')
        return result

    def __setitem__(self, key, value):
        """Store any Python object into an abstract database object."""
        return self.put(key, value)

    def put(self, key, value):
        """Store a string record into an abstract database object."""
        result = tc.adb_put2(self.db, key, value)
        if not result:
            self._raise('Error putting a string record in an abstract ' \
                            'database object')
        return result

    def putkeep(self, key, value):
        """Store a new string record into an abstract database object."""
        return tc.adb_putkeep2(self.db, key, value)

    def putcat(self, key, value):
        """Concatenate a string value at the end of the existing
        record in an abstract database object."""
        result = tc.adb_putcat2(self.db, key, value)
        if not result:
            self._raise('Error concatenating a string value in an abstract ' \
                            'database object')
        return result

    def __delitem__(self, key):
        """Remove a Python object of an abstract database object."""
        return self.out(key)

    def out(self, key):
        """Remove a string record of an abstract database object."""
        result = tc.adb_out2(self.db, key)
        if not result:
            self._raise('Error deleting a string record from an abstract ' \
                            'database object.');
        return result

    def __getitem__(self, key):
        """Retrieve a Python object in an abstract database object."""
        return self._getitem(key)

    def _getitem(self, key):
        """Retrieve a string record in an abstract database object."""
        value = tc.adb_get2(self.db, key)
        if not value:
            raise KeyError(key)
        return value.value

    def get(self, key, default=None):
        """Retrieve a string record in an abstract database object."""
        try:
            value = self._getitem(key)
        except KeyError:
            value = default
        return value

    def vsiz(self, key, as_raw=False):
        """Get the size of the value of a string record in an abstract
        database object."""
        result = tc.adb_vsiz2(self.db, key)
        if result == -1:
            self._raise('Error getting the size of a string record in an ' \
                            ' abstract database object.');
        return result

    def keys(self):
        """Get all the keys of an abstract database object."""
        return list(self.iterkeys())

    def iterkeys(self):
        """Iterate for every key in an abstract database object."""
        if not tc.adb_iterinit(self.db):
            self._raise('Error initializing the iterator of an abstract ' \
                            'database object.')
        while True:
            key = tc.adb_iternext2(self.db)
            if not key:
                break
            yield key.value

    def values(self):
        """Get all the values of an abstract database object."""
        return list(self.itervalues())

    def itervalues(self):
        """Iterate for every value in an abstract database object."""
        if not tc.adb_iterinit(self.db):
            self._raise('Error initializing the iterator of an abstract ' \
                            'database object.')
        while True:
            key = tc.adb_iternext2(self.db)
            if not key:
                break
            value = tc.adb_get2(self.db, key)
            yield value.value

    def items(self):
        """Get all the items of an abstract database object."""
        return list(self.iteritems())

    def iteritems(self):
        """Iterate for every key / value in an abstract database
        object."""
        if not tc.adb_iterinit(self.db):
            self._raise('Error initializing the iterator of an abstract ' \
                            'database object.')
        while True:
            key = tc.adb_iternext2(self.db)
            if not key:
                break
            value = tc.adb_get2(self.db, key)
            yield (key.value, value.value)

    def __iter__(self):
        """Iterate for every key in an abstract database object."""
        return self.iterkeys()

    def fwmkeys(self, prefix, max_=-1):
        """Get forward matching string keys in an abstract database
        object."""
        tclist_objs = tc.adb_fwmkeys2(self.db, prefix, max_)
        if not tclist_objs:
            self._raise('Error forward matching string keys in an abstract ' \
                            'database object.')
        return util.deserialize_tclist(tclist_objs, str)

    def sync(self):
        """Synchronize updated contents of an abstract database object
        with the file and the device."""
        result = tc.adb_sync(self.db)
        if not result:
            self._raise('Error synchronizing with an abstract database object.')
        return result

    def optimize(self, params):
        """Optimize the storage of an abstract database object."""
        result = tc.adb_optimize(self.db, params)
        if not result:
            self._raise('Error optimizing the storage of an abstract ' \
                            'database object.')
        return result

    def vanish(self):
        """Remove all records of an abstract database object."""
        result = tc.adb_vanish(self.db)
        if not result:
            self._raise('Error removing all records of an abstract ' \
                            'database object.')
        return result

    def copy(self, path):
        """Copy the database file of an abstract database object."""
        result = tc.adb_copy(self.db, path)
        if not result:
            self._raise('Error coping the database file of an abstract ' \
                            'database object.')
        return result

    def tranbegin(self):
        """Begin the transaction of an abstract database object."""
        result = tc.adb_tranbegin(self.db)
        if not result:
            self._raise('Error beginning the transaction of an abstract ' \
                            'database object.')
        return result

    def trancommit(self):
        """Commit the transaction of an abstract database object."""
        result = tc.adb_trancommit(self.db)
        if not result:
            self._raise('Error committing the transaction of an abstract ' \
                            'database object.')
        return result

    def tranabort(self):
        """Abort the transaction of an abstract database object."""
        result = tc.adb_tranabort(self.db)
        if not result:
            self._raise('Error aborting the transaction of an abstract ' \
                            'database object.')
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
        """Get the file path of an abstract database object."""
        result = tc.adb_path(self.db)
        if not result:
            self._raise('Error getting the file path of an abstract ' \
                            'database object.')
        return result

    def __len__(self):
        """Get the number of records of an abstract database object."""
        return tc.adb_rnum(self.db)

    def size(self):
        """Get the size of the database of an abstract database
        object."""
        result = tc.adb_size(self.db)
        if not result:
            self._raise('Error getting the size of the database of an ' \
                            'abstract database object.')
        return result

    def misc(self, name, args):
        """"Call a versatile function for miscellaneous operations of
        an abstract database object."""
        tclist_objs = tc.adb_misc(self.db, name, args)
        if not tclist_objs:
            self._raise('Error calling a versatile function for ' \
                            'miscellaneous operations of an abstract ' \
                            'database object.')
        return util.deserialize_objs(tclist_objs)

    def omode(self):
        """Get the open mode of an abstract database object."""
        return tc.adb_omode(self.db)

    def reveal(self):
        """Get the concrete database object of an abstract database
        object."""
        return tc.adb_reveal(self.db)

    # def putproc(self, key, value, proc, op):
    #     """Store a record into an abstract database object with a
    #     duplication handler."""
    #     # See tc.adb_putproc

    def foreach(self, proc, op):
        """Process each record atomically of an abstract database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, str)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, str)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.adb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            self._raise('Error processing each record atomically of an ' \
                            'abstract database object.')
        return result

    def __contains__(self, key):
        """Return True if abstract database object has the key."""
        return self.has_key(key)

    def has_key(self, key):
        """Return True if abstract database object has the key."""
        result = False
        value = tc.adb_get2(self.db, key)
        if value:
            result = True
        return result

    def _raise(self, msg=None):
        """Raise an exception based on the internal database object."""
        mode = self.omode()
        if mode == OMDB:
            msg = 'Error in hash memory abstract database object.'
        elif mode == ONDB:
            msg = 'Error in B+ tree memory abstract database object.'
        elif mode == OHDB:
            msg = tc.hdb_errmsg(tc.hdb_ecode(self.reveal()))
        elif mode == OBDB:
            msg = tc.bdb_errmsg(tc.bdb_ecode(self.reveal()))
        elif mode == OFDB:
            msg = tc.fdb_errmsg(tc.fdb_ecode(self.reveal()))
        elif mode == OTDB:
            msg = tc.tdb_errmsg(tc.tdb_ecode(self.reveal()))
        raise tc.TCException(msg)


class ADB(ADBSimple):
    def __init__(self):
        """Create an abstract database object."""
        ADBSimple.__init__(self)

    def put(self, key, value, raw_key=False, raw_value=False):
        """Store any Python object into an abstract database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.adb_put(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            self._raise('Error putting a Python object in an abstract ' \
                            'database object')
        return result

    def put_str(self, key, value, as_raw=False):
        """Store a string record into an abstract database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.put(key, value, as_raw, True)

    def put_unicode(self, key, value, as_raw=False):
        """Store an unicode string record into an abstract database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.put(key, value, as_raw, True)

    def put_int(self, key, value, as_raw=False):
        """Store an integer record into an abstract database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.put(key, value, as_raw, True)

    def put_float(self, key, value, as_raw=False):
        """Store a double precision record into an abstract database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.put(key, value, as_raw, True)

    def putkeep(self, key, value, raw_key=False, raw_value=False):
        """Store a new Python object into an abstract database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        return tc.adb_putkeep(self.db, c_key, c_key_len, c_value, c_value_len)

    def putkeep_str(self, key, value, as_raw=False):
        """Store a new string record into an abstract database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_unicode(self, key, value, as_raw=False):
        """Store a new unicode string record into an abstract database
        object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_int(self, key, value, as_raw=False):
        """Store a new integer record into an abstract database
        object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self.putkeep(key, value, as_raw, True)

    def putkeep_float(self, key, value, as_raw=False):
        """Store a new double precision record into an abstract
        database object."""
        assert isinstance(value, float), 'Value is not a float'
        return self.putkeep(key, value, as_raw, True)

    def putcat(self, key, value, raw_key=False, raw_value=False):
        """Concatenate an object value at the end of the existing
        record in an abstract database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = util.serialize(value, raw_value)
        result = tc.adb_putcat(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            self._raise('Error concatenating a Python object in an abstract ' \
                            'database object')
        return result

    def putcat_str(self, key, value, as_raw=False):
        """Concatenate a string value at the end of the existing
        record in an abstract database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self.putcat(key, value, as_raw, True)

    def putcat_unicode(self, key, value, as_raw=False):
        """Concatenate an unicode string value at the end of the
        existing record in an abstract database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self.putcat(key, value, as_raw, True)

    def out(self, key, as_raw=False):
        """Remove a Python object of an abstract database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.adb_out(self.db, c_key, c_key_len)
        if not result:
            self._raise('Error deleting a Python object in an abstract ' \
                            'database object.');
        return result

    def _getitem(self, key, raw_key=False, value_type=None):
        """Retrieve a Python object in an abstract database object."""
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, c_value_len) = tc.adb_get(self.db, c_key, c_key_len)
        if not c_value:
            raise KeyError(key)
        return util.deserialize(c_value, c_value_len, value_type)

    def get(self, key, default=None, raw_key=False, value_type=None):
        """Retrieve a Python object in an abstract database object."""
        try:
            value = self._getitem(key, raw_key, value_type)
        except KeyError:
            value = default
        return value

    def get_str(self, key, default=None, as_raw=False):
        """Retrieve a string record in an abstract database object."""
        return self.get(key, default, as_raw, str)

    def get_unicode(self, key, default=None, as_raw=False):
        """Retrieve an unicode string record in a abstract database
        object."""
        return self.get(key, default, as_raw, unicode)

    def get_int(self, key, default=None, as_raw=False):
        """Retrieve an integer record in an abstract database object."""
        return self.get(key, default, as_raw, int)

    def get_float(self, key, default=None, as_raw=False):
        """Retrieve a double precision record in an abstract database
        object."""
        return self.get(key, default, as_raw, float)

    def vsiz(self, key, as_raw=False):
        """Get the size of the value of a Python object in an abstract
        database object."""
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.adb_vsiz(self.db, c_key, c_key_len)
        if result == -1:
            self._raise('Error getting the size of a Python object in an ' \
                            ' abstract database object.');
        return result

    def keys(self, as_type=None):
        """Get all the keys of an abstract database object."""
        return list(self.iterkeys(as_type))

    def iterkeys(self, as_type=None):
        """Iterate for every key in an abstract database object."""
        if not tc.adb_iterinit(self.db):
            self._raise('Error initializing the iterator of an abstract ' \
                            'database object.')
        while True:
            c_key, c_key_len = tc.adb_iternext(self.db)
            if not c_key:
                break
            key = util.deserialize(c_key, c_key_len, as_type)
            yield key

    def values(self, as_type=None):
        """Get all the values of an abstract database object."""
        return list(self.itervalues(as_type))

    def itervalues(self, as_type=None):
        """Iterate for every value in an abstract database object."""
        if not tc.adb_iterinit(self.db):
            self._raise('Error initializing the iterator of an abstract ' \
                            'database object.')
        while True:
            c_key, c_key_len = tc.adb_iternext(self.db)
            if not c_key:
                break
            (c_value, c_value_len) = tc.adb_get(self.db, c_key, c_key_len)
            value = util.deserialize(c_value, c_value_len, as_type)
            yield value

    def items(self, key_type=None, value_type=None):
        """Get all the items of an abstract database object."""
        return list(self.iteritems(key_type, value_type))

    def iteritems(self, key_type=None, value_type=None):
        """Iterate for every key / value in an abstract database
        object."""
        if not tc.adb_iterinit(self.db):
            self._raise('Error initializing the iterator of an abstract ' \
                            'database object.')
        while True:
            c_key, c_key_len = tc.adb_iternext(self.db)
            if not c_key:
                break
            (c_value, c_value_len) = tc.adb_get(self.db, c_key, c_key_len)
            key = util.deserialize(c_key, c_key_len, key_type)
            value = util.deserialize(c_value, c_value_len, value_type)
            yield (key, value)

    def fwmkeys(self, prefix, max_=-1, as_raw=True):
        """Get forward matching string keys in an abstract database
        object."""
        (c_prefix, c_prefix_len) = util.serialize(prefix, as_raw)
        tclist_objs = tc.adb_fwmkeys(self.db, c_prefix, c_prefix_len, max_)
        if not tclist_objs:
            self._raise('Error forward matching string keys in an abstract ' \
                            'database object.')
        as_type = util.get_type(prefix, as_raw)
        return util.deserialize_tclist(tclist_objs, as_type)

    def add_int(self, key, num, as_raw=False):
        """Add an integer to a record in an abstract database object."""
        assert isinstance(num, int), 'Value is not an integer'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.adb_addint(self.db, c_key, c_key_len, num)
        if not result:
            self._raise('Error adding an integer to a record in an abstract ' \
                            'database object.')
        return result

    def add_float(self, key, num, as_raw=False):
        """Add a real number to a record in an abstract database object."""
        assert isinstance(num, float), 'Value is not a float'
        (c_key, c_key_len) = util.serialize(key, as_raw)
        result = tc.adb_adddouble(self.db, c_key, c_key_len, num)
        if not result:
            self._raise('Error adding a real number to a record in an ' \
                            'abstract database object.')
        return result

    def foreach(self, proc, op, key_type=None, value_type=None):
        """Process each record atomically of an abstract database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize(ctypes.cast(c_key, ctypes.c_void_p),
                                   c_key_len, key_type)
            value = util.deserialize(ctypes.cast(c_value, ctypes.c_void_p),
                                     c_value_len, value_type)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.adb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            self._raise('Error processing each record atomically of an ' \
                            'abstract database object.')
        return result

    def has_key(self, key, raw_key=False):
        """Return True if abstract database object has the key."""
        result = False
        (c_key, c_key_len) = util.serialize(key, raw_key)
        (c_value, _) = tc.adb_get(self.db, c_key, c_key_len)
        if c_value:
            result = True
        return result
