# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import shelve
import shutil
import anydbm
import datetime
import os
import os.path
import select
import threading

class BaseMultiHashDriver(object):
    """
    Base multihash driver class. Multihash driver is like dictionary of
    dictionaries, it stores multiple dictionaries (hashes) accessible by key
    string. Each hash is read only, to modify use save() method passing new
    dictionary or sequence of (key, value) to it.
    """

    def load(self, hashkey):
        """
        Loads hash associated with hashkey. If no hash found raises KeyError.

        @param hashkey: hash key string
        @return: read only dictionary like object
        """
        raise KeyError(hashkey)

    def get_mtime(self, hashkey):
        """
        Returns hash modification time (last save time). Raises KeyError if no
        hash found.

        @param hashkey: hash key string
        @return: datetime.datetime object of last modification

        """
        raise KeyError(hashkey)

    def save(self, hashkey, newhash, blocking=True):
        """
        Creates new hash or overrides existing. New hash initialized by newhash
        that is dictionary or sequence of (key, value).

        If any concurrent thread/process already updates hash and blocking is
        True, then call to this method sleeps until other thread/process finish
        hash updating. If blocking is False and concurrent write access was
        detected, returns False.

        @param hashkey: hash key string
        @param newhash: dictionary or sequence of (key, value) to initialize
                        new hash
        @keyword blocking: use blocking or unblocking call
        @return: True if hash was saved, otherwise False
        """
        raise KeyError(hashkey)

    def modify(self, hashkey, otherhash, blocking=True):
        """
        Updates hash with values in otherhash that is dictionary or sequence of
        (key, value).

        @param hashkey: hash key string
        @param otherhash: dictionary or sequence of (key, value) to update
                          hash from
        @keyword blocking: use blocking or unblocking call
        @return: True if hash was modified, otherwise False
        """
        raise KeyError(hashkey)

class MultiHashInFilesMixin:
    """
    Mixin class for multihash drivers that use files to store hash objects.
    """
    def __init__(self, filename, max_lock_time = None, no_excl = False):
        """
        @param filename: file name to use for hash files (string or callable)
        @param max_lock_time: maximum lock time in seconds or as
                              datetime.timedelta object
        @param no_excl: disable usage of O_EXCL flag when locking
        """
        self.filename = filename
        if max_lock_time is None:
            max_lock_time = datetime.timedelta(seconds = 600)
        elif type(max_lock_time) in (int, long, float):
            max_lock_time = datetime.timedelta(seconds = max_lock_time)
        self.max_lock_time = max_lock_time
        self.no_excl = no_excl

    def get_filename(self, hashkey):
        filename = self.filename
        if callable(filename):
            filename = filename(hashkey)
        elif 'XXX' in filename:
            filename = filename.replace('XXX', hashkey)
        else:
            filename += hashkey
        return filename

    def get_new_filename(self, real_filename):
        return real_filename + '.new'

    def get_lock_filename(self, real_filename):
        return real_filename + '.lock'

    def save_with_locking(self, hashkey, newhash, blocking, do_save):
        real_filename = self.get_filename(hashkey)
        lock_filename = self.get_lock_filename(real_filename)
        new_filename = self.get_new_filename(real_filename)
        error = None
        loop_cnt = 0

        while True:
            loop_cnt += 1
            if self.no_excl:
                # if usage of O_EXCL flag is disabled
                try:
                    fd = os.open(lock_filename, os.O_RDONLY)
                except OSError:
                    fd = os.open(lock_filename, os.O_CREAT)
                    break
            else:
                # locking using O_EXCL flag
                try:
                    fd = os.open(lock_filename, os.O_CREAT | os.O_EXCL)
                except OSError, e:
                    error = e
                else:
                    break
                try:
                    fd = os.open(lock_filename, os.O_RDONLY)
                except OSError:
                    if loop_cnt >= 3:
                        raise error
                    continue
            try:
                # check lock time
                lock_time = datetime.datetime.fromtimestamp(os.fstat(fd).st_ctime)
                if lock_time + self.max_lock_time <= datetime.datetime.now():
                    os.unlink(lock_filename)
                    continue
                if not blocking:
                    return False
                # wait until lock file was removed
                select.select((), (), (fd,), 5)
            finally:
                os.close(fd)
        try:
            # save data to newly created file, then just move it to the real
            # file, so that other precesses/threads can read old data while new
            # data is not completely written
            do_save(real_filename, new_filename, newhash)
            try:
                shutil.move(new_filename, real_filename)
            except IOError:
                # in some cases db module appends '.db' suffix to the file name
                # when saving...
                if (not os.path.exists(new_filename) and
                        os.path.exists(new_filename + '.db')):
                    shutil.move(new_filename + '.db', real_filename)
                else:
                    raise
        finally:
            os.close(fd)
            os.unlink(lock_filename)
        return True

class MemMultiHashDriver(BaseMultiHashDriver):
    """
    Memory multihash driver.

    >>> drv = MemMultiHashDriver()
    >>> drv.save('foo', dict(bar = 3))
    True
    >>> drv.load('foo')['bar']
    3
    """
    def __init__(self):
        self.db = {}
        self.db_mtime = {}
        self.db_lock = threading.Lock()

    def load(self, hashkey):
        return self.db[hashkey]

    def get_mtime(self, hashkey):
        return self.db_mtime[hashkey]

    def save(self, hashkey, newhash, blocking=True):
        result = self.db_lock.acquire(blocking)
        if not result:
            return False
        try:
            if isinstance(newhash, dict):
                newhash = newhash.copy()
            else:
                newhash = dict(newhash)
            self.db[hashkey] = newhash
            self.db_mtime[hashkey] = datetime.datetime.now()
        finally:
            self.db_lock.release()
        return True

    def modify(self, hashkey, otherhash, blocking=True):
        result = self.db_lock.acquire(blocking)
        if not result:
            return False
        try:
            if not isinstance(otherhash, dict):
                otherhash = dict(otherhash)
            self.db.setdefault(hashkey, {})
            self.db[hashkey].update(otherhash)
            self.db_mtime[hashkey] = datetime.datetime.now()
        finally:
            self.db_lock.release()
        return True

class ShelveMultiHashDriver(BaseMultiHashDriver, MultiHashInFilesMixin):
    """
    Multihash driver that use shelve module to store hashes.

    >>> import os
    >>> import os.path
    >>> filename = 'shelve_multihash_test_XXX.db'
    >>> os.path.exists(filename.replace('XXX', 'foo'))
    False
    >>> drv = ShelveMultiHashDriver(filename)
    >>> drv.save('foo', dict(bar = 3))
    True
    >>> os.path.exists(filename.replace('XXX', 'foo'))
    True
    >>> drv.load('foo')['bar']
    3
    >>> def test_generator():
    ...   for i in range(100):
    ...     if i == 5:
    ...       x = drv.save('foo', dict(bar = 3), blocking = False)
    ...       assert x == False
    ...     yield ('bar%d' % i, i)
    >>> drv.save('foo', test_generator())
    True
    >>> drv.load('foo')['bar55']
    55
    >>> os.unlink(filename.replace('XXX', 'foo'))
    """
    def __init__(self, filename, max_lock_time = None, no_excl = False,
            db_module = None):
        """
        @param filename: file name to use for hash files (string or callable)
        @keyword max_lock_time: maximum lock time in seconds or as
                                datetime.timedelta object
        @keyword no_excl: disable usage of O_EXCL flag when locking
        @keyword db_module: DBM module to use
        """
        MultiHashInFilesMixin.__init__(self, filename, max_lock_time, no_excl)
        if isinstance(db_module, basestring):
            db_module = __import__(db_module)
        self.db_module = db_module

    def load(self, hashkey):
        try:
            return shelve.open(self.get_filename(hashkey), 'r')
        except anydbm.error:
            raise KeyError(hashkey)

    def get_mtime(self, hashkey):
        try:
            return datetime.datetime.fromtimestamp(os.stat(
                self.get_filename(hashkey)).st_mtime)
        except OSError:
            raise KeyError(hashkey)

    def save(self, hashkey, newhash, blocking=True):
        def do_save(real_filename, new_filename, newhash):
            if isinstance(newhash, dict):
                newhash = newhash.items()
            if self.db_module:
                # if appropriate db module is specified, use it to create empty
                # database
                db = self.db_module.open(new_filename, 'n')
                db.sync()
                db = shelve.open(new_filename, 'w')
            else:
                db = shelve.open(new_filename, 'n')
            for k, v in newhash:
                db[k] = v
            db.sync()
        return self.save_with_locking(hashkey, newhash, blocking, do_save)

    def modify(self, hashkey, otherhash, blocking=True):
        def do_modify(real_filename, new_filename, newhash):
            if isinstance(newhash, dict):
                newhash = newhash.items()
            try:
                shutil.copy(real_filename, new_filename)
            except IOError:
                if self.db_module:
                    db = self.db_module.open(new_filename, 'n')
                    db.sync()
                    db = shelve.open(new_filename, 'w')
                else:
                    db = shelve.open(new_filename, 'n')
            else:
                db = shelve.open(new_filename, 'w')
            for k, v in newhash:
                db[k] = v
            db.sync()
        return self.save_with_locking(hashkey, otherhash, blocking, do_modify)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
