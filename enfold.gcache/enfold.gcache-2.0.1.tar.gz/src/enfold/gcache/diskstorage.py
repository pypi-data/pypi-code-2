################################################################################
#
# Copyright: Enfold Systems, LLC
# $Id: diskstorage.py 4292 2010-08-30 19:57:37Z nikolay $
#
# The first version of this code used 'shelve', which behind the scenes
# used the old bsddb interface.  The current version of the code directly
# uses the newer bsddb.db interface, including explicit DBEnv() management,
# in the hope that later we can also move the 'priority queue' functionality
# into bsddb, protect data integrity using transactions, and thus make it
# possible for multiple processes to access the cache.
# We also had a very crude recovery system - if we got a db error opening
# the cache or a DB_RUNRECOVERY accessing it, we clobbered the cache and
# reopened it.  We no longer do that - we attempt to use bsddb recovery
# mechanisms, and if the cache is totally screwed it must be removed
# externally (eg, by the admin) - we don't just clobber this data!
###############################################################################
"""A disk-storage for our generic cache."""
import os
import urllib
import shutil
import errno
import sys
import time

from hashlib import md5
from cPickle import dump, dumps, loads

from bsddb import hashopen, db
from bsddb.dbutils import DeadlockWrap

try:
    import winerror
except ImportError: # Not on Windows
    class winerror:
        ERROR_SHARING_VIOLATION = 32
        ERROR_ACCESS_DENIED = 5
        EACCES = None

from interfaces import Uncachable


class DiskStorage(object):
    """ A cache storage - provides a mapping interface for the cache.  This
    implementation keeps a shelve, but stores each individual item in its ownfile.
    Specifically, in the cache directory, there is a file 'index'.  This is
    a shelve of all the metadata for the cache.  There is also a directory
    'data' - inside this is one file for each key in the cache.  This filename
    is calculated based on the md5 hash of the key and is stored back in the
    metadata in a 'storage_id' slot. """

    # Max number of files in our 'files in use' queue.
    MAX_FILE_DELETE_QUEUE = 1000

    # Max number of seconds we should continue to try and remove the file.  If
    # its still in use after this period we give up on it and the file will end
    # up an 'orphan' on the file-system
    MAX_FILE_DELETE_QUEUE_TIME = 600 # track for 10 minutes.

    def __init__(self, directory, logger):
        assert os.path.isdir(directory)

        self.logger = logger
        self.return_files = False
        self._failed_files = [] # list of files we failed to remove.

        # bsddb etc don't understand unicode - encode the directory name
        # for the filesystem (and all children of that dir use ascii)
        directory = directory.encode(sys.getfilesystemencoding())
        self.directory = os.path.abspath(directory)
        self.data_directory = os.path.join(self.directory, "data")
        self.open()

        logger.info("Cache database has %d entries", len(self.data))

    def __len__(self):
        return len(self.data)

    @classmethod
    def get_data_dirs(cls):
        """Return a list of relative sub-directories that hold the cache.  Callers
        may use this list to check if a cache is already in place or to
        remove the cache
        """
        return ["data", "meta"]

    def purge_iter(self):
        """ Deal with a "purge list" - we store it in the database, as bsddb is
        damn fast.  We optimize the "list empty" condition as this is the
        usual case."""
        if self.have_purge_entries:
            c = self.purge_table.cursor()
            got = c.first()
            while got:
                yield got[1]
                got = c.next()

    def purge_add(self, value):
        DeadlockWrap(self.purge_table.append, value)
        self.have_purge_entries = True

    def purge_remove(self, value):
        assert self.have_purge_entries
        c = self.purge_table.cursor()
        got = c.first()
        while got:
            if got[1] == value:
                c.delete()
                break
        self.have_purge_entries = len(self.purge_table) != 0

    def iterkeys(self, start = None):
        """ A specialized key iterator: if param is given, start the iteration
        from the first matching key """
        # XXX - if we use DB_INIT_LOCK, this may deadlock - it appears
        # we can not keep a cursor opened while other DB operations are
        # performed.
        c = self.data.cursor()
        if start is None:
            got = c.first()
        else:
            got = c.set_range(start)
        while got:
            yield got[0]
            got = c.next()

    def open(self):
        """ Attempt to open an existing cache.  If forceNew is True, then the
        cache will be clobbered and initialized, otherwise we attempt to
        check if it is valid and only clobber if necessary."""
        logger = self.logger

        db_dir = os.path.join(self.directory, "meta")
        if not os.path.isdir(db_dir):
            logger.info("Creating new cache database at '%s'", db_dir)
            os.mkdir(db_dir)

        self.env = e = db.DBEnv()
        e.set_lk_detect(db.DB_LOCK_DEFAULT) # deadlock detection
        # Stick with DB_PRIVATE while we are limited to 1 process per cache
        # As we still use a local lock, we can avoid DB_INIT_LOCK
        # which prevents us needing to carefully close cursors etc.
        flags = db.DB_PRIVATE | db.DB_CREATE | db.DB_THREAD | db.DB_INIT_MPOOL
        e.open(db_dir, flags)

        self.data = db.DB(e)
        self.data.open("metadata", db.DB_BTREE, db.DB_CREATE, 0666)

        # purge table - using a 'recno' database so we get append semantics
        # This could still do with optimization though.
        self.purge_table = db.DB(e)
        self.purge_table.open("purge", db.DB_RECNO, db.DB_CREATE, 0666)
        self.have_purge_entries = len(self.purge_table) != 0

        if not os.path.isdir(self.data_directory):
            os.mkdir(self.data_directory)

    def close(self):
        try:
            self.data.close()
        except:
            exc_val = sys.exc_info()[1]
            self.logger.error("Failed to close the database: %s", exc_val)
        self.data = None

        try:
            self.purge_table.close()
        except:
            exc_val = sys.exc_info()[1]
            self.logger.error("Failed to close the purge_table: %s", exc_val)
        self.purge_table = None

        try:
            self.env.close()
        except:
            exc_val = sys.exc_info()[1]
            self.logger.error(
                "Failed to close the database environment: %s", exc_val)
        self.env = None

    def flush(self):
        self.data.sync()

    def _get_filename(self, key, meta):
        """ Get the filename for an existing item.  The filename is generally
        stored in the meta-data - however, old caches did not store
        a filename, but instead just used the (quoted) key directly.
        So if no filename is in the metadata, we use the key the old way."""
        mf = meta.storage_id
        if mf is None:
            base = urllib.quote(key, "")
        else:
            base = mf
        return os.path.join(self.data_directory, base)

    def _calc_new_filename(self, key):
        """ Calculate a new, unique filename for a key.
        First just try an md5 hash.  Collissions should be rare - but
        if we find one, we append a timestamp.  Collissions should be rarer
        still - but we still handle that by allowing up to 100 unique
        filenames per hash, per timestamp.  After that we give up in disgust."""
        base = md5(key).hexdigest()
        name = os.path.join(self.data_directory, base)
        if not os.path.exists(name):
            return base

        # Name exists - probably hash collission
        self.logger.info(
            "Hashed filename for key %r exists - adding timestamp", key)
        base = base + "-" + str(time.clock()) + "-"
        for i in xrange(100):
            base = base + str(i)
            name = os.path.join(self.data_directory, base)
            if not os.path.exists(name):
                return base

        # So - we have 100 filenames all with the same hash *and* the
        # same timestamp - something must be very wrong!
        raise Uncachable("Can't create a unique filename for key %r" % (key,))

    def _load_(self, fp):
        """ A cache that only needed to handle strings/BLOBS could be more
        efficient by overriding these methods and dumping the string
        directly to the file."""
        return loads(fp.read())

    def _dump_(self, data, fp):
        dump(data, fp)

    def __getitem__(self, key):
        # return meta, data
        meta = self.get_meta(key)
        fname = self._get_filename(key, meta)
        try:
            fp = open(fname, "rb")
            if self.return_files:
                data = fp
            else:
                data = self._load_(fp)
                fp.close()
        except EnvironmentError, details:
            self.logger.error("Failed to read cache-file '%s' - %s",fname,details)
            # We do *not* remove our meta-data - the cache itself needs it
            # to correctly dispose of us when the time is right - but it
            # does the dispose by using 'get_meta', so will not see this
            # in that case (ie, only the consumer of the cache should see this
            # KeyError).
            raise KeyError, key
        return meta, data

    def __setitem__(self, key, (meta, data)):
        # If no filename exists, allocate one.  meta may already have a
        # filename if we are updating an existing item.
        if meta.storage_id is None:
            meta.storage_id= self._calc_new_filename(key)

        fname = os.path.join(self.data_directory, meta.storage_id)
        try:
            fp = open(fname, "wb")
        except EnvironmentError, details:
            # This happens when the filename is too large!
            # This should not happen now we use md5 digests for the filename
            # but it conceivably if the directory name was insanely long
            # So for now this code can remain...
            # (Note: using the short version of the parent would be an option)
            if os.name=='nt' and len(fname) > 260: # MAX_PATH=260
                # this is a hard limit using the crt!  Just treat as uncachable.
                self.logger.info(
                    "Can't cache '%s' - as the filename is too long.  "
                    "Consider changing the cache directory to a path "
                    "with a shorter name.")
                raise Uncachable, "Filename too long"

            # Otherwise - someone may have nuked our directory from under
            # us in a crude attempt at clearing the cache - handle that.
            if details.errno != errno.ENOENT:
                raise
            self.logger.warning(
                "Cache directory vanished - attempting to re-create")
            os.makedirs(os.path.dirname(fname))
            fp = open(fname, "wb")

        self._dump_(data, fp)
        fp.close()
        DeadlockWrap(self.data.put, key, dumps((meta, None), 2))

    def get_meta(self, key):
        """ The extra methods our cache wants. """
        self.logger.log(1, "Loading %r metadata from DB", key)
        sval = DeadlockWrap(self.data.get, key)
        if sval is None:
            raise KeyError(key)
        self.logger.log(1, "Load complete")
        return loads(sval)[0]

    def update_meta(self, key, meta):
        # We *must* raise a KeyError if the item doesn't exist!
        existing = DeadlockWrap(self.data.get, key)
        if existing is None:
            raise KeyError(key)
        # existing[1] is always null in our impl, but later that may change..
        DeadlockWrap(self.data.put, key, dumps((meta, existing[1]), 2))

    CACHE_FILE_REMOVED = 0
    CACHE_FILE_IN_USE = 1
    CACHE_FILE_ERROR = 2
    def _remove_cache_file(self, fname):
        """Removes a cached file.  If the file can't be removed, that is
        probably because someone is currently using it

        Returns one of the constants above.
        """
        try:
            os.unlink(fname)
            self.logger.debug("Deleted cache file '%s'", fname)
            return self.CACHE_FILE_REMOVED
        except os.error, why:
            errnum = getattr(why, 'winerror', why.errno)
            if errnum in (winerror.ERROR_SHARING_VIOLATION,
                          winerror.ERROR_ACCESS_DENIED, errno.EACCES):
                self.logger.debug(
                    "cache-file in use - will remove later (%s)", fname)
                return self.CACHE_FILE_IN_USE
            else:
                self.logger.warning(
                    "Failed to delete cache file '%s': %s", fname, why)
                return self.CACHE_FILE_ERROR

    def __delitem__(self, key):
        fname = self._get_filename(key, self.get_meta(key))
        if self._remove_cache_file(fname) == self.CACHE_FILE_IN_USE:
            if len(self._failed_files) > self.MAX_FILE_DELETE_QUEUE:
                self.logger.warning(
                    "Too many files in removal queue - %s will be orphaned",
                    fname)
            else:
                self._failed_files.append((fname, time.time()))
        DeadlockWrap(self.data.delete, key)
    # XXX - override all value methods!

    def maintain(self):
        # This can all be done without locks by relying on the GIL.
        # * We push a 'sentinal' (None) to the end of the list.
        # * We loop, poping the start and disposing of it, or if we fail to
        #   dispose, push it at the back of the list.
        # * When we pop None, we stop.
        # If multiple threads are running, each thread may see a different
        # thread's sentinal None - but that's OK - so long as each thread sees
        # exactly one, there's no problem.
        if not self._failed_files:
            return

        self._failed_files.append((None, None)) # our sentinal

        now = time.time()
        while 1:
            fname, when = self._failed_files.pop(0)
            if fname is None:
                # a sentinal
                break
            # try and remove it again.
            if self._remove_cache_file(fname) != self.CACHE_FILE_IN_USE:
                # either worked, or failed in a way we give up on.
                continue
            # So - we failed again to nuke it.  Should we re-add it for
            # consideration next time we are called?
            if now - when > self.MAX_FILE_DELETE_QUEUE_TIME:
                self.logger.warning(
                    "Timeout trying to delete old cache file %s - this file will be orphaned.",
                    fname)
            elif len(self._failed_files) > self.MAX_FILE_DELETE_QUEUE:
                self.logger.warning(
                    "Too many files in removal queue - %s will be orphaned",
                    fname)
            else:
                # ok - we will try again.
                self._failed_files.append((fname, when))
