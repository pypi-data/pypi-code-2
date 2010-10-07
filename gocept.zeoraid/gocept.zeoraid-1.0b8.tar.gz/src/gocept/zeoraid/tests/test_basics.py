##############################################################################
#
# Copyright (c) 2007-2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test harness for gocept.zeoraid."""

from ZEO.tests import forker, ThreadTests
from ZEO.tests.testZEO import get_port
from ZODB.tests import RevisionStorage, PersistentStorage
from ZODB.tests import MTStorage, ReadOnlyStorage, RecoveryStorage
from ZODB.tests import StorageTestBase, BasicStorage
from ZODB.tests import Synchronization, ConflictResolution, HistoryStorage
from ZODB.tests import TransactionalUndoStorage, PackableStorage
from gocept.zeoraid.tests.loggingstorage import LoggingStorage
import ZConfig
import ZEO.runzeo
import ZODB.MappingStorage
import ZODB.config
import ZODB.interfaces
import gocept.zeoraid.storage
import gocept.zeoraid.tests.test_recovery
import mock
import os
import random
import shutil
import stat
import tempfile
import threading
import time
import transaction
import unittest
import zc.lockfile
import zope.interface.verify
import StringIO

# import logging
# logging.getLogger().setLevel(0)
# logging.getLogger().addHandler(logging.StreamHandler())


def fail(obj, name):
    old_method = getattr(obj, name)

    def failing_method(*args, **kw):
        setattr(obj, name, old_method)
        raise Exception()
    setattr(obj, name, failing_method)


class MockStorage(ZODB.MappingStorage.MappingStorage):

    def __init__(self, undo):
        super(MockStorage, self).__init__()
        self.undo = undo

    def supportsUndo(self):
        return self.undo


class Opener(object):

    def __init__(self, name, undo=True):
        self.name = name
        self.undo = undo

    def open(self):
        return MockStorage(self.undo)


class ZEOStorageBackendTests(StorageTestBase.StorageTestBase):

    def open(self, **kwargs):
        self._storage = gocept.zeoraid.storage.RAIDStorage(
            'teststorage', self._storages, **kwargs)

    def setUp(self):
        self._server_storage_files = []
        self._servers = []
        self._pids = []
        self._storages = []
        for i in xrange(5):
            port = get_port()
            zconf = forker.ZEOConfig(('', port))
            zport, adminaddr, pid, path = forker.start_zeo_server(
                self.getConfig(), zconf, port)
            self._pids.append(pid)
            self._servers.append(adminaddr)
            self._storages.append(gocept.zeoraid.testing.ZEOOpener(
                str(i), zport, storage='1', wait=False))
        self.open()

    def getConfig(self):
        filename = self.__fs_base = tempfile.mktemp()
        self._server_storage_files.append(filename)
        return """\
        <filestorage 1>
        path %s
        </filestorage>
        """ % filename

    def tearDown(self):
        self._storage.close()
        for server in self._servers:
            forker.shutdown_zeo_server(server)
        for pid in self._pids:
            os.waitpid(pid, 0)
        for file in self._server_storage_files:
            if os.path.exists(file):
                os.unlink(file)


class ReplicationStorageTests(BasicStorage.BasicStorage,
        TransactionalUndoStorage.TransactionalUndoStorage,
        RevisionStorage.RevisionStorage,
        PackableStorage.PackableStorage,
        PackableStorage.PackableUndoStorage,
        Synchronization.SynchronizedStorage,
        ConflictResolution.ConflictResolvingStorage,
        ConflictResolution.ConflictResolvingTransUndoStorage,
        HistoryStorage.HistoryStorage,
        PersistentStorage.PersistentStorage,
        MTStorage.MTStorage,
        ReadOnlyStorage.ReadOnlyStorage,
        ):

    def check_raid_interfaces(self):
        for iface in (ZODB.interfaces.IStorage,
                      ZODB.interfaces.IBlobStorage,
                      ZODB.interfaces.IStorageUndoable,
                      ZODB.interfaces.IStorageCurrentRecordIteration,

                      # The IServable interface allows to not implement the
                      # `lastInvalidations` method. We chose to do this and
                      # can't verify the interface formally due to that.
                      # ZEO.interfaces.IServeable,
                      ):
            self.assert_(zope.interface.verify.verifyObject(iface,
                                                            self._storage))

    def check_getname(self):
        self.assertEquals('teststorage', self._storage.getName())
        self._storage.close()
        self.assertEquals('teststorage', self._storage.getName())


class FailingStorageTestSetup(StorageTestBase.StorageTestBase):

    backend_count = 3
    cluster_mode = 'coop'

    def _backend(self, index):
        return self._storage.storages[
            self._storage.storages_optimal[index]]

    def setUp(self):
        self.temp_paths = []
        self._servers = []
        self._storages = []
        self._pids = []
        for i in xrange(self.backend_count):
            port = get_port()
            zconf = forker.ZEOConfig(('', port))
            zport, adminaddr, pid, path = forker.start_zeo_server(
                """%import gocept.zeoraid.tests
                <failingstorage 1>
                </failingstorage>""",
                zconf, port)
            self._pids.append(pid)
            blob_dir = tempfile.mkdtemp()
            self.temp_paths.append(blob_dir)
            self._servers.append(adminaddr)
            self._storages.append(gocept.zeoraid.testing.ZEOOpener(
                str(i), zport, storage='1', cache_size=12,
                blob_dir=blob_dir, min_disconnect_poll=0.5, wait=1,
                wait_timeout=60))
        blob_dir = tempfile.mkdtemp()
        self.temp_paths.append(blob_dir)
        self._storage = gocept.zeoraid.storage.RAIDStorage(
            'teststorage', self._storages,
            cluster_mode=self.cluster_mode, blob_dir=blob_dir)

        self.orig_choice = random.choice
        random.choice = lambda seq: seq[0]

    def tearDown(self):
        self._storage.close()
        for server in self._servers:
            forker.shutdown_zeo_server(server)
        for pid in self._pids:
            os.waitpid(pid, 0)
        for path in self.temp_paths:
            shutil.rmtree(path)

        random.choice = self.orig_choice


class FailingStorageSharedBlobTestSetup(FailingStorageTestSetup):

    def setUp(self):
        self.temp_paths = []
        self._servers = []
        self._storages = []
        self._pids = []
        blob_dir = tempfile.mkdtemp()
        for i in xrange(self.backend_count):
            port = get_port()
            zconf = forker.ZEOConfig(('', port))
            zport, adminaddr, pid, path = forker.start_zeo_server(
                """%%import gocept.zeoraid.tests
                <failingstorage 1>
                  blob-dir %s
                </failingstorage>""" % blob_dir,
                zconf, port)
            self._pids.append(pid)
            self._servers.append(adminaddr)
            self._storages.append(gocept.zeoraid.testing.ZEOOpener(
                str(i), zport, storage='1', cache_size=12, blob_dir=blob_dir,
                shared_blob_dir=True, min_disconnect_poll=0.5, wait=1,
                wait_timeout=60))
        self._storage = gocept.zeoraid.storage.RAIDStorage(
            'teststorage', self._storages, blob_dir=blob_dir,
            cluster_mode=self.cluster_mode, shared_blob_dir=True)

        self.orig_choice = random.choice
        random.choice = lambda seq: seq[0]


class FailingStorageTestBase(object):

    def _disable_storage(self, index):
        self._storage.raid_disable(self._storage.storages_optimal[index])

    def test_apply_storage_disconnect(self):
        backend_name = self._storage.storages_optimal[0]
        backend_storage = self._storage.storages[backend_name]
        backend_storage.close()

        reliable, oid = self._storage._apply_storage(
            backend_name, 'new_oid')
        self.assertEquals(False, reliable)
        self.assertEquals([backend_name], self._storage.storages_degraded)

    def test_close(self):
        self._storage.close()
        self.assertEquals(self._storage.closed, True)
        # Calling close() multiple times is allowed (and a no-op):
        self._storage.close()
        self.assertEquals(self._storage.closed, True)

    def test_close_degrading(self):
        # See the comment on `test_close_failing`.
        backend = self._backend(0)
        backend.close = raise_exception
        self._storage.close()
        self.assertEquals(True, self._storage.closed)
        del backend.close
        backend.close()

    def test_close_failing(self):
        # Even though we make the server-side storage fail, we do not
        # receive an error or a degradation because the result of the failure
        # is that the connection is closed. This is actually what we wanted.
        # Unfortunately that means that an error can be hidden while closing.
        backend0 = self._backend(0)
        backend1 = self._backend(1)
        backend0.close = raise_exception
        backend1.close = raise_exception
        self._storage.close()
        self.assertEquals(True, self._storage.closed)
        del backend0.close
        del backend1.close
        backend0.close()
        backend1.close()

    def test_close_server_missing(self):
        # See the comment on `test_close_failing`.
        forker.shutdown_zeo_server(self._servers[0])
        del self._servers[0]
        self._storage.close()
        self.assertEquals([], self._storage.storages_degraded)
        self.assertEquals(True, self._storage.closed)

    def test_getsize(self):
        self.assertEquals(4, self._backend(0).getSize())
        self.assertEquals(4, self._backend(1).getSize())
        self.assertEquals(4, self._storage.getSize())
        self._storage.close()
        # getSize() always returns a value to allow clients to connect even
        # when the RAID is failed.
        self.assertEquals(0, self._storage.getSize())

    def test_getsize_degrading(self):
        self._backend(0).fail('getSize')
        # This doesn't get noticed because ClientStorage already knows
        # the answer and caches it. Therefore calling getSize can never
        # degrade or fail a RAID.
        self.assertEquals(4, self._storage.getSize())
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(1).fail('getSize')
        self.assertEquals(4, self._storage.getSize())
        self.assertEquals('optimal', self._storage.raid_status())

    def test_history(self):
        oid = self._storage.new_oid()
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(0).history, oid, '')
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(1).history, oid, '')
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._storage.history, oid, '')
        self.assertEquals('optimal', self._storage.raid_status())

        self._dostore(oid=oid)
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals(1, len(self._backend(1).history(oid, '')))
        self.assertEquals(1, len(self._storage.history(oid, '')))

        self._disable_storage(0)
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals(1, len(self._storage.history(oid, '')))
        self.assertEquals('degraded', self._storage.raid_status())

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.history, oid, '')
        self.assertEquals('failed', self._storage.raid_status())

    def test_history_degrading(self):
        oid = self._storage.new_oid()
        self._dostore(oid=oid)
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals(1, len(self._backend(1).history(oid, '')))
        self.assertEquals(1, len(self._storage.history(oid, '')))

        self._backend(0).fail('history')
        self.assertEquals(1, len(self._storage.history(oid, '')))
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('history')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.history, oid, '')
        self.assertEquals('failed', self._storage.raid_status())

    def test_lastTransaction(self):
        self.assertEquals(None, self._storage.lastTransaction())
        self.assertEquals(None, self._backend(0).lastTransaction())
        self.assertEquals(None, self._backend(1).lastTransaction())
        self._dostore()
        lt = self._storage.lastTransaction()
        self.assertNotEquals(None, lt)
        self.assertEquals(lt, self._backend(0).lastTransaction())
        self.assertEquals(lt, self._backend(1).lastTransaction())

    def test_lastTransaction_degrading(self):
        self._disable_storage(0)
        self.assertEquals(None, self._storage.lastTransaction())
        self._disable_storage(0)
        self.assertEquals('failed', self._storage.raid_status())
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.lastTransaction)

    def test_len_degrading(self):
        # Brrrr. ClientStorage doesn't seem to implement __len__ correctly.
        self.assertEquals(0, len(self._storage))
        self.assertEquals(0, len(self._backend(0)))
        self.assertEquals(0, len(self._backend(1)))
        self.assertEquals
        self._dostore(
            revid='\x00\x00\x00\x00\x00\x00\x00\x01')
        # See above. This shouldn't be 0 if ClientStorage worked correctly.
        self.assertEquals(1, len(self._storage))
        self.assertEquals(1, len(self._backend(0)))
        self.assertEquals(1, len(self._backend(1)))

        self._disable_storage(0)
        self._dostore(
            revid='\x00\x00\x00\x00\x00\x00\x00\x02')
        # See above. This shouldn't be 0 if ClientStorage worked correctly.
        self.assertEquals(2, len(self._storage))
        self.assertEquals(2, len(self._backend(0)))

        self._disable_storage(0)
        self.assertEquals(0, len(self._storage))

    def test_load_store_degrading1(self):
        oid = self._storage.new_oid()
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._storage.load, oid)
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(0).load, oid)
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(1).load, oid)

        self._dostore(oid=oid, revid='\x00\x00\x00\x00\x00\x00\x00\x01')
        data_record, serial = self._storage.load(oid)
        self.assertEquals(
            '((U\x10ZODB.tests.MinPOq\x01U\x05MinPOq\x02tq\x03Nt.}'
            'q\x04U\x05valueq\x05K\x07s.', data_record)
        self.assertEquals(self._storage.lastTransaction(), serial)
        self.assertEquals((data_record, serial), self._backend(0).load(oid))
        self.assertEquals((data_record, serial), self._backend(1).load(oid))

        self._disable_storage(0)
        self.assertEquals((data_record, serial), self._storage.load(oid))
        self.assertEquals((data_record, serial), self._backend(0).load(oid))

        oid = self._storage.new_oid()
        self._dostore(oid=oid, revid='\x00\x00\x00\x00\x00\x00\x00\x02')
        data_record, serial = self._storage.load(oid)
        self.assertEquals(self._storage.lastTransaction(), serial)
        self.assertEquals((data_record, serial), self._backend(0).load(oid))

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.load, oid)

    def test_load_can_be_failed(self):
        # ClientStorage does not directly call `load` but
        # `loadEx` which in turn calls `load` on the storage.
        # Unfortunately `storage.load` is also rebound onto the storage
        # server so in the future the fail() might not work. To avoid
        # hard-to-debug errors in the future, we test that fail('load')
        # actually does make the `load` call fail.
        oid = self._storage.new_oid()
        self._backend(0).fail('load')
        self.assertRaises(Exception, self._backend(0).load, oid)

    def test_load_degrading2(self):
        # If this test fails weirdly, please check that the test above works
        # correctly before losing hair.
        oid = self._storage.new_oid()
        self._dostore(oid=oid, revid='\x00\x00\x00\x00\x00\x00\x00\x01')
        self._backend(0).fail('load')
        data_record, serial = self._storage.load(oid)
        self.assertEquals(
            '((U\x10ZODB.tests.MinPOq\x01U\x05MinPOq\x02tq\x03Nt.}'
            'q\x04U\x05valueq\x05K\x07s.', data_record)
        self.assertEquals(self._storage.lastTransaction(), serial)
        self.assertEquals((data_record, serial), self._backend(0).load(oid))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('load')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.load, oid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_loadBefore_degrading1(self):
        oid = self._storage.new_oid()
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._storage.loadBefore, oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(0).loadBefore,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(1).loadBefore,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertEquals('optimal', self._storage.raid_status())

        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        revid2 = self._dostoreNP(oid=oid, revid=revid, data='bar')
        data_record, serial, end_tid = self._storage.loadBefore(oid, revid2)
        self.assertEquals('foo', data_record)
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(1).loadBefore(oid, revid2))

        self._disable_storage(0)
        self.assertEquals((data_record, serial, end_tid),
                          self._storage.loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.loadBefore, oid, revid2)

    def test_loadBefore_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        revid2 = self._dostoreNP(oid=oid, revid=revid, data='bar')
        data_record, serial, end_tid = self._storage.loadBefore(oid, revid2)
        self.assertEquals('foo', data_record)
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(1).loadBefore(oid, revid2))

        self._backend(0).fail('loadBefore')
        self.assertEquals((data_record, serial, end_tid),
                          self._storage.loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('loadBefore')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.loadBefore, oid, revid2)
        self.assertEquals('failed', self._storage.raid_status())

    def test_loadSerial_degrading1(self):
        oid = self._storage.new_oid()
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._storage.loadSerial,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(0).loadSerial,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(1).loadSerial,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertEquals('optimal', self._storage.raid_status())

        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        self._dostoreNP(oid=oid, revid=revid, data='bar')

        data_record = self._storage.loadSerial(oid, revid)
        self.assertEquals('foo', data_record)
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(1).loadSerial(oid, revid))

        self._disable_storage(0)
        self.assertEquals(data_record,
                          self._storage.loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.loadSerial, oid, revid)

    def test_loadSerial_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        self._dostoreNP(oid=oid, revid=revid, data='bar')

        data_record = self._storage.loadSerial(oid, revid)
        self.assertEquals('foo', data_record)
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(1).loadSerial(oid, revid))
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(0).fail('loadSerial')
        self.assertEquals(data_record,
                          self._storage.loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('loadSerial')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.loadSerial, oid, revid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_new_oid_degrading1(self):
        self.assertEquals(8, len(self._storage.new_oid()))
        self._disable_storage(0)
        self.assertEquals(8, len(self._storage.new_oid()))
        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.new_oid)

    def test_new_oid_degrading2(self):
        self.assertEquals(8, len(self._storage.new_oid()))
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(0)._oids = None
        self._backend(0).fail('new_oid')
        self.assertEquals(8, len(self._storage.new_oid()))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0)._oids = None
        self._backend(0).fail('new_oid')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.new_oid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_new_oid_unsynchronised_degrading(self):
        name = self._backend(1).getName()
        self._backend(0).new_oid()
        oid = self._storage.new_oid()
        self.assertEquals('\x00\x00\x00\x00\x00\x00\x00\x01', oid)
        self.assertEquals('degraded', self._storage.raid_status())
        self.assertEquals(name, self._backend(0).getName())

    def test_pack_degrading1(self):
        # We store differently sized data for each revision so that packing
        # definitely yields different file sizes.
        # We work on the root object to avoid garbage collection
        # kicking in.
        oid = ZODB.utils.z64
        revid = self._dostore(oid=oid, revid=None, data=1)
        revid2 = self._dostore(oid=oid, revid=revid, data=2)

        self.assertEquals(256, self._backend(0).getSize())
        self.assertEquals(256, self._backend(1).getSize())
        self.assertEquals(256, self._storage.getSize())

        self._storage.pack(time.time(), ZODB.serialize.referencesf)
        self.assertEquals(130, self._backend(0).getSize())
        self.assertEquals(130, self._backend(1).getSize())
        self.assertEquals(130, self._storage.getSize())

        revid3 = self._dostore(oid=oid, revid=revid2, data=3)
        self.assertEquals(256, self._backend(0).getSize())
        self.assertEquals(256, self._backend(1).getSize())
        self.assertEquals(256, self._storage.getSize())

        self._disable_storage(0)
        self._storage.pack(time.time(), ZODB.serialize.referencesf)
        self.assertEquals(130, self._backend(0).getSize())
        self.assertEquals(130, self._storage.getSize())

        self._dostore(oid=oid, revid=revid3, data=4)
        self.assertEquals(256, self._storage.getSize())
        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.pack,
                          time.time(), ZODB.serialize.referencesf)

    def test_pack_degrading2(self):
        # We store differently sized data for each revision so that packing
        # definitely yields different file sizes.
        # We work on the root object to avoid garbage collection
        # kicking in.
        oid = ZODB.utils.z64
        revid = self._dostore(oid=oid, revid=None, data=1)
        revid2 = self._dostore(oid=oid, revid=revid, data=2)
        self.assertEquals(256, self._storage.getSize())

        self._backend(0).fail('pack')
        self._storage.pack(time.time(), ZODB.serialize.referencesf)
        self.assertEquals(130, self._backend(0).getSize())
        self.assertEquals(130, self._storage.getSize())
        self.assertEquals('degraded', self._storage.raid_status())

        revid3 = self._dostore(oid=oid, revid=revid2, data=3)
        self.assertEquals(256, self._backend(0).getSize())
        self.assertEquals(256, self._storage.getSize())

        self._backend(0).fail('pack')
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.pack,
                          time.time(), ZODB.serialize.referencesf)
        self.assertEquals('failed', self._storage.raid_status())

    def test_store_degrading2(self):
        oid = ZODB.utils.z64

        self._backend(0).fail('store')
        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('store')
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._dostoreNP,
                          oid=oid, revid=revid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_begin_degrading(self):
        self._backend(0).fail('tpc_begin')
        oid = self._storage.new_oid()
        self._dostoreNP(oid=oid, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        oid = self._storage.new_oid()
        self._backend(0).fail('tpc_begin')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._dostoreNP, oid=oid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_vote_degrading(self):
        self._backend(0).fail('tpc_vote')
        oid = self._storage.new_oid()
        self._dostoreNP(oid=oid, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        oid = self._storage.new_oid()
        self._backend(0).fail('tpc_vote')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._dostoreNP, oid=oid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_finish_degrading(self):
        self._backend(0).fail('tpc_finish')
        oid = self._storage.new_oid()
        self._dostoreNP(oid=oid, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        oid = self._storage.new_oid()
        self._backend(0).fail('tpc_finish')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._dostoreNP, oid=oid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_abort_not_degrading(self):
        # tpc_abort (in combination with ClientStorage) will never cause
        # degradation, even if it raises an exception.
        # This is because of an asynchronous call made by ClientStorage.
        # For us this is ok. If there really is something wrong with the
        # storage, we'll know in the next synchronous call.
        self._backend(0).fail('tpc_abort')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.tpc_abort(t)
        # tpc_abort is asynchronous. We make another synchronous call to make
        # sure that it was already executed.
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self.assertEquals('optimal', self._storage.raid_status())

    def store_blob(self, blob_file_name=None):
        oid = self._storage.new_oid()
        if blob_file_name is None:
            handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'wb').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        tid = self._storage.lastTransaction()
        return oid, tid

    def test_blob_usage(self):
        oid, tid = self.store_blob()
        stored_file_name = self._storage.loadBlob(oid, tid)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'rb').read())
        expected = self._storage.blob_fshelper.getBlobFilename(oid, tid)
        self.assertEquals(expected, stored_file_name)

        # Check that a blob isn't loaded twice now that it's in the cache.
        old_mtime = os.stat(stored_file_name)[stat.ST_MTIME]
        time.sleep(1) # mtime has a granularity of 1 second
        stored_file_name = self._storage.loadBlob(oid, tid)
        new_mtime = os.stat(stored_file_name)[stat.ST_MTIME]
        self.assertEquals(old_mtime, new_mtime)

    def test_storeBlob_degrading1(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._disable_storage(0)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading1_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._disable_storage(0)
        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.storeBlob,
                          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)

    def test_storeBlob_degrading2(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._backend(0).fail('storeBlob')
        # The server doesn't call its storage's storeBlob right away but only
        # when tpc_vote ist called.
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertEquals('optimal', self._storage.raid_status())
        self._storage.tpc_vote(t)
        self.assertEquals('degraded', self._storage.raid_status())
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading2_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._backend(0).fail('storeBlob')
        self._backend(1).fail('storeBlob')
        # The server doesn't call its storage's storeBlob right away but only
        # when tpc_vote ist called.
        self._storage.storeBlob(
            oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.tpc_vote, t)

    def test_storeBlob_degrading3(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)

        def fail(*args, **kw):
            raise Exception()
        self._backend(0).storeBlob = fail
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertEquals('degraded', self._storage.raid_status())
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading3_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)

        def fail(*args, **kw):
            raise Exception()
        self._backend(0).storeBlob = fail
        self._backend(1).storeBlob = fail
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.storeBlob,
                          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)

    def test_loadBlob_degrading1(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        last_transaction = self._storage.lastTransaction()

        # Find file name, clean up cache.
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        os.remove(stored_file_name)

        self._disable_storage(0)
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

        # Clean up cache.
        os.remove(stored_file_name)

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.loadBlob, oid, last_transaction)

    def test_loadBlob_degrading2(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        last_transaction = self._storage.lastTransaction()

        # Clear cache.
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        os.unlink(stored_file_name)
        b0_filename = self._backend(0).loadBlob(oid, last_transaction)
        os.unlink(b0_filename)

        self._backend(0).fail('loadBlob')
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())
        self.assertEquals('degraded', self._storage.raid_status())

        # Clear cache.
        os.unlink(stored_file_name)
        b0_filename = self._backend(0).loadBlob(oid, last_transaction)
        os.unlink(b0_filename)

        self._backend(0).fail('loadBlob')
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.loadBlob, oid, last_transaction)
        self.assertEquals('failed', self._storage.raid_status())

    def test_storeBlob_temporary_files(self):
        tmp = tempfile.mkdtemp()
        self.assertEquals([], os.listdir(tmp))
        self.store_blob(os.path.join(tmp, 'foo'))
        self.assertEquals([], os.listdir(tmp))

    def test_temporaryDirectory(self):
        working_dir = tempfile.mkdtemp()
        storage = ZODB.config.storageFromString("""
        %%import gocept.zeoraid
        <raidstorage>
          blob-dir %(wd)s/blobs
          <filestorage foo>
            path %(wd)s/Data.fs
          </filestorage>
        </raidstorage>
        """ % {'wd': working_dir})
        self.assertEquals(os.path.join(working_dir, 'blobs', 'tmp'),
                          storage.temporaryDirectory())
        self.assert_(os.path.isdir(storage.temporaryDirectory()))
        self.assert_(storage.blob_fshelper.isSecure(
            storage.temporaryDirectory()))
        shutil.rmtree(working_dir)

    def test_readonly(self):
        working_dir = tempfile.mkdtemp()
        self.temp_paths.append(working_dir)

        storage = ZODB.config.storageFromString("""
        %%import gocept.zeoraid
        <raidstorage>
          read-only false
          <filestorage foo>
            path %(wd)s/Data.fs
          </filestorage>
        </raidstorage>
        """ % {'wd': working_dir})
        self.assertEquals(False, storage.isReadOnly())
        storage.close()

        storage = ZODB.config.storageFromString("""
        %%import gocept.zeoraid
        <raidstorage>
          read-only true
          <filestorage foo>
            path %(wd)s/Data.fs
          </filestorage>
        </raidstorage>
        """ % {'wd': working_dir})
        self.assertEquals(True, storage.isReadOnly())
        storage.close()

    def test_supportsUndo_required(self):
        self.assertRaises(RuntimeError,
                          gocept.zeoraid.storage.RAIDStorage,
                          'name', [Opener('1', undo=False)])

    def test_supportsUndo(self):
        self.assertEquals(True, self._storage.supportsUndo())

    def test_undo_degrading1(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='23')
        revid = self._dostoreNP(oid, revid=revid, data='24')
        revid = self._dostoreNP(oid, revid=revid, data='25')

        obj = self._storage.load(oid, '')
        self.assertEquals('25', obj[0])

        # First try: undo with one disabled storage
        info = self._storage.undoInfo()
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._disable_storage(0)
        self._storage.undo(info[0]['id'], t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)

        # Second try: undo with both storages disabled
        info = self._storage.undoInfo()
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.undo, info[2]['id'], t)

    def test_undo_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='23')
        revid = self._dostoreNP(oid, revid=revid, data='24')
        revid = self._dostoreNP(oid, revid=revid, data='25')

        obj = self._storage.load(oid, '')
        self.assertEquals('25', obj[0])

        # First try: undo with one disabled storage
        info = self._storage.undoInfo()
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._backend(0).fail('undo')
        self._storage.undo(info[0]['id'], t)
        self.assertEquals('degraded', self._storage.raid_status())
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)

        # Second try: undo with both storages disabled
        info = self._storage.undoInfo()
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._backend(0).fail('undo')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.undo, info[2]['id'], t)
        self.assertEquals('failed', self._storage.raid_status())

    def test_undoLog_degrading1(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='23')
        revid = self._dostoreNP(oid, revid=revid, data='24')

        obj = self._storage.load(oid, '')
        self.assertEquals('24', obj[0])

        self._disable_storage(0)
        info = self._storage.undoLog()
        self.assertEquals(2, len(info))

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.undoLog)

    def test_undoLog_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='23')
        revid = self._dostoreNP(oid, revid=revid, data='24')

        obj = self._storage.load(oid, '')
        self.assertEquals('24', obj[0])

        self._backend(0).fail('undoLog')
        info = self._storage.undoLog()
        self.assertEquals('degraded', self._storage.raid_status())
        self.assertEquals(2, len(info))

        self._backend(0).fail('undoLog')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.undoLog)
        self.assertEquals('failed', self._storage.raid_status())

    def test_undoInfo_degrading1(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='23')
        revid = self._dostoreNP(oid, revid=revid, data='24')

        obj = self._storage.load(oid, '')
        self.assertEquals('24', obj[0])

        self._disable_storage(0)
        info = self._storage.undoInfo()
        self.assertEquals(2, len(info))

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.undoInfo)

    def test_undoInfo_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='23')
        revid = self._dostoreNP(oid, revid=revid, data='24')

        obj = self._storage.load(oid, '')
        self.assertEquals('24', obj[0])

        self._backend(0).fail('undoInfo')
        info = self._storage.undoInfo()
        self.assertEquals('degraded', self._storage.raid_status())
        self.assertEquals(2, len(info))

        self._backend(0).fail('undoInfo')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.undoInfo)
        self.assertEquals('failed', self._storage.raid_status())

    def test_record_iternext(self):
        for x in range(5):
            oid = self._storage.new_oid()
            self._dostoreNP(oid, data=str(x))

        oid, serial, data, next = self._storage.record_iternext(None)
        self.assertEquals('0', data)
        oid, serial, data, next = self._storage.record_iternext(next)
        self.assertEquals('1', data)
        oid, serial, data, next = self._storage.record_iternext(next)
        self.assertEquals('2', data)
        oid, serial, data, next = self._storage.record_iternext(next)
        self.assertEquals('3', data)
        oid, serial, data, next = self._storage.record_iternext(next)
        self.assertEquals('4', data)
        self.assertEquals(None, next)

    def test_record_iternext_degrading1(self):
        for x in range(5):
            oid = self._storage.new_oid()
            self._dostoreNP(oid, data=str(x))

        self._disable_storage(0)
        oid, serial, data, next = self._storage.record_iternext(None)
        self.assertEquals('0', data)

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.record_iternext, next)

    def test_record_iternext_degrading2(self):
        for x in range(5):
            oid = self._storage.new_oid()
            self._dostoreNP(oid, data=str(x))

        self._backend(0).fail('record_iternext')
        oid, serial, data, next = self._storage.record_iternext(None)
        self.assertEquals('0', data)
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('record_iternext')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.record_iternext, next)
        self.assertEquals('failed', self._storage.raid_status())

    def test_gettid_degrading1(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='foo')

        self._disable_storage(0)
        tid = self._storage.getTid(oid)
        self.assertEquals(revid, tid)

        self._disable_storage(0)
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.getTid, oid)

    def test_gettid_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid, data='foo')

        self._backend(0).fail('getTid')
        tid = self._storage.getTid(oid)
        self.assertEquals(revid, tid)
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('getTid')
        self.assertRaises(ZEO.Exceptions.ClientStorageError, self._storage.getTid, oid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_transaction_finishing(self):
        self.assertEquals(None, self._storage.tpc_transaction())
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self.assertEquals(t, self._storage.tpc_transaction())
        self._storage.tpc_vote(t)
        self.assertEquals(t, self._storage.tpc_transaction())
        self._storage.tpc_finish(t)
        self.assertEquals(None, self._storage.tpc_transaction())

    def test_tpc_transaction_aborting(self):
        self.assertEquals(None, self._storage.tpc_transaction())
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self.assertEquals(t, self._storage.tpc_transaction())
        self._storage.tpc_vote(t)
        self.assertEquals(t, self._storage.tpc_transaction())
        self._storage.tpc_abort(t)
        self.assertEquals(None, self._storage.tpc_transaction())

    def test_getExtensionMethods(self):
        methods = self._storage.getExtensionMethods()
        self.assertEquals(dict(raid_details=None,
                               raid_disable=None,
                               raid_recover=None,
                               raid_status=None,
                               raid_reload=None),
                          methods)

    def test_getExtensionMethods_degrading(self):
        self._disable_storage(0)
        self._storage.getExtensionMethods()
        self._disable_storage(0)
        self._storage.getExtensionMethods()

    def test_recover(self):
        self._dostore()
        self._dostore()
        self._dostore()
        self._disable_storage(0)
        self._dostore()
        self._dostore()
        self._storage.raid_recover(
            self._storage.storages_degraded[0], sync=True)
        self.assertEquals('optimal', self._storage.raid_status())
        gocept.zeoraid.tests.test_recovery.compare(
            self, self._backend(0), self._backend(1))
        self._storage.new_oid()
        self.assertEquals('optimal', self._storage.raid_status())
        # Make sure we can still write to the RAID.
        self._dostore()
        self.assertEquals('optimal', self._storage.raid_status())

    def test_recover_failing(self):
        self._dostore()
        self._dostore()
        self._dostore()
        self._disable_storage(0)
        self.assertEquals('degraded', self._storage.raid_status())
        # Store something regularly
        self._dostore()
        self._dostore()
        # Store something in the wrong storage which will cause recovery to
        # fail
        other = self._storage.openers['1'].open()
        raid = self._storage
        self._storage = other
        self._dostore()
        self._dostore()
        self._storage.close()
        self._storage = raid

        self.assertRaises(
            ValueError,
            self._storage._recover_impl, self._storage.storages_degraded[0])
        values = self._storage.raid_details().values()
        self.assertEquals(
            1,
            values.count('failed: An error occured recovering the storage'))
        self.assertEquals(self.backend_count-1, values.count('optimal'))

    def test_timeoutBackend(self):
        self._storage.timeout = 2

        def slow_tpc_begin(*args):
            time.sleep(4)
        self._backend(0).tpc_begin = slow_tpc_begin
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self.assertEquals('degraded', self._storage.raid_status())

    def test_reload_without_zeo(self):
        self.assertRaises(RuntimeError, self._storage.raid_reload)


class FailingStorageCoopTests(FailingStorageTestBase,
                              FailingStorageTestSetup):

    def test_blob_cache_cannot_link(self):
        called_broken = []

        def broken_link(foo, bar):
            called_broken.append(True)
            raise OSError

        oid, tid = self.store_blob()
        good_link = os.link
        os.link = broken_link
        try:
            stored_file_name = self._storage.loadBlob(oid, tid)
            self.assertEquals([True], called_broken)
            self.assertEquals('I am a happy blob.',
                              open(stored_file_name, 'rb').read())
        finally:
            os.link = good_link

    def test_blob_cache_locking(self):
        return_value = []

        def try_loadBlob():
            return_value.append(self._storage.loadBlob(oid, tid))

        oid, tid = self.store_blob()
        stored_file_name = self._storage.loadBlob(oid, tid)
        os.remove(stored_file_name)
        lock_filename = stored_file_name + '.lock'

        # Test race condition that the lock is held during loadBlob() but the
        # file isn't put in place by the other party.
        lock = zc.lockfile.LockFile(lock_filename)
        thread = threading.Thread(target=try_loadBlob)
        thread.start()
        time.sleep(0.5)
        self.assert_(thread.isAlive())
        lock.close()
        os.remove(lock_filename)
        time.sleep(0.5)
        self.assert_(not thread.isAlive())
        self.assertEquals([None], return_value)

        # Test race condition that the lock is held during loadBlob() and the
        # file is put in place correctly by the other party.
        return_value = []
        lock = zc.lockfile.LockFile(lock_filename)
        thread = threading.Thread(target=try_loadBlob)
        thread.start()
        time.sleep(0.5)
        self.assert_(thread.isAlive())
        blob_file = open(stored_file_name, 'wb')
        blob_file.write('I am an unhappy blob.')
        blob_file.close()
        lock.close()
        os.remove(lock_filename)
        time.sleep(0.5)
        self.assert_(not thread.isAlive())
        self.assertEquals([stored_file_name], return_value)
        self.assertEquals('I am an unhappy blob.',
                          open(stored_file_name, 'rb').read())

        thread.join()


class FailingStorageSingleTests(FailingStorageCoopTests):

    backend_count = 2
    cluster_mode = 'single'


class FailingStorageCoopSharedBlobTests(FailingStorageTestBase,
                                        FailingStorageSharedBlobTestSetup):

    def test_loadBlob_file_missing(self):
        oid, tid = self.store_blob()
        stored_file_name = self._storage.loadBlob(oid, tid)
        os.remove(stored_file_name)
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._storage.loadBlob, oid, tid)

    def test_loadBlob_degrading1(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        last_transaction = self._storage.lastTransaction()

        self._disable_storage(0)
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

        self._disable_storage(0)
        self.assertEquals('failed', self._storage.raid_status())

        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_loadBlob_degrading2(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        last_transaction = self._storage.lastTransaction()

        self._backend(0).fail('loadBlob')
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(1).fail('loadBlob')
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())
        self.assertEquals('optimal', self._storage.raid_status())

    def test_storeBlob_degrading2(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        fail(self._backend(0), 'storeBlob')
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertEquals('degraded', self._storage.raid_status())
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading2_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        fail(self._backend(0), 'storeBlob')
        fail(self._backend(1), 'storeBlob')
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          self._storage.storeBlob,
                          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)


class FailingStorageSingleSharedBlobTests(FailingStorageCoopSharedBlobTests):

    backend_count = 2
    cluster_mode = 'single'


class ZEOReplicationStorageTests(ZEOStorageBackendTests,
                                 ReplicationStorageTests,
                                 ThreadTests.ThreadTests):

    def checkInterfaces(self):
        # Overwrite this method because it tests all interfaces while we want
        # to exclude IServeable which has a method that is described as
        # optional in the doc string.
        pass

    def check_startup_missing_zeo_does_not_block(self):
        forker.shutdown_zeo_server(self._servers[0])
        self._storage.close()
        self.open()
        self.assertEquals('degraded', self._storage.raid_status())
        # We should still be able to write
        oid = self._storage.new_oid()
        self._dostore(oid=oid, data='0', already_pickled=True)
        # Remove closed ZEO server to allow correct shutdown.
        del self._servers[0]


def raise_exception():
    raise Exception()


class LoggingStorageOpener(object):

    def __init__(self, name, **kwargs):
        self.name = name
        self.file_handle, self.file_name = tempfile.mkstemp()

    def open(self, **kwargs):
        return LoggingStorage(self.name, self.file_name)


class LoggingStorageDistributedTests(unittest.TestCase):

    def test_distributed_single_calls(self):
        raid = mock.Mock()
        raid.closed = False
        raid.storages_optimal = ['1', '2']
        raid._apply_storage = mock.Mock(return_value=(True, 5))
        op = gocept.zeoraid.storage.SingleStorageOperation(raid)
        for i in xrange(20):
            op.getSize()
        self.assertEqual(20, raid._apply_storage.call_count)
        counts = {}
        for item in raid._apply_storage.call_args_list:
            storage = item[0][0]
            counts[storage] = counts.get(storage, 0) + 1
        self.assertEqual(['1', '2'], sorted(counts.keys()))
        self.assert_(counts['1'] > 2)
        self.assert_(counts['2'] > 2)


class ExtensionMethodsTests(ZEOStorageBackendTests):

    def open(self):
        self.zeo_configfile = tempfile.mktemp()
        self._server_storage_files.append(self.zeo_configfile)
        self.update_config()

        options = ZEO.runzeo.ZEOOptions()
        options.realize(['-C', self.zeo_configfile])
        zeo = ZEO.runzeo.ZEOServer(options)
        zeo.open_storages()
        self._storage = zeo.storages['teststorage']

    def update_config(self):
        # create a config file and save it
        file_contents = """\
            %%import gocept.zeoraid
            <zeo>
                address 127.0.0.1:%s
            </zeo>

            <raidstorage teststorage>
            """ % get_port()

        for count, storage in enumerate(self._storages):
            file_contents += """\
                <zeoclient %s>
                    server %s:%s
                    storage 1
                </zeoclient>
            """ % (storage.name, self._servers[count][0],
                   (self._servers[count][1] - 1))

        file_contents += """\
            </raidstorage>
            """

        f = open(self.zeo_configfile, 'w')
        f.write(file_contents)
        f.close()

    def test_reload_add(self):
        self.assertEquals(len(self._storage.openers), 5)
        self.assertEquals([], self._storage.storages_degraded)

        # set up a new backend
        port = get_port()
        zconf = forker.ZEOConfig(('', port))
        zport, adminaddr, pid, path = forker.start_zeo_server(self.getConfig(),
                                                              zconf, port)
        self._pids.append(pid)
        self._servers.append(adminaddr)
        self._storages.append(gocept.zeoraid.testing.ZEOOpener(
            '5', zport, storage='1', min_disconnect_poll=0.5, wait=1,
            wait_timeout=60))

        # configure the RAID to use the new backend
        self.update_config()
        self._storage.raid_reload()

        self.assertEquals(len(self._storage.openers), 6)
        self.assertEquals(['5'], self._storage.storages_degraded)

        # ensure that we can still write to the RAID
        oid = self._storage.new_oid()
        self._dostore(oid=oid, data='0', already_pickled=True)

        # recover the newly added backend
        self._storage.raid_recover('5', sync=True)
        self.assertEquals([], self._storage.storages_degraded)

        # ensure that we can still write to the RAID
        oid2 = self._storage.new_oid()
        self._dostore(oid=oid2, data='1', already_pickled=True)
        self.assertEquals([], self._storage.storages_degraded)

        # ensure that all transactions are available from the new backend
        self.assertEquals('5', self._storages[-1].name)
        s5 = self._storages[-1].open()
        self.assertEquals('0', s5.load(oid)[0])
        self.assertEquals('1', s5.load(oid2)[0])

        s5.close()

    def test_recover_same_storage(self):
        # This is a somewhat convoluted example for accidentally connecting a
        # new storage to the same ZEO server that is already used and trying
        # to recover. This will almost recover but will cause the newly
        # connected storage to be disconnected again because OIDs can't be
        # synchronized.
        removed_storage = self._storages.pop(3)

        # configure the RAID to no longer use the removed backend
        self.update_config()
        self._storage.raid_reload()
        self.assertEquals({'1': 'optimal', '0': 'optimal', '2': 'optimal',
                           '4': 'optimal'},
                          self._storage.raid_details())

        # Re-insert the storage
        self._storages.append(removed_storage)
        self.update_config()
        self._storage.raid_reload()
        self.assertEquals({'1': 'optimal', '0': 'optimal',
                           '3': 'failed: added by controller', '2': 'optimal',
                           '4': 'optimal'},
                          self._storage.raid_details())

        self._storage.raid_recover('3')

        while self._storage.raid_status() != 'degraded':
            time.sleep(0.1)
        # This is unobvious: Storage 4 fails because the _apply_all call for
        # new_oid causes storage 4 to give an inconsistent result thus being
        # dropped from the pool of good storages. Storage 3 however meets the
        # OID target then thus being picked up.
        self.assertEquals({'1': 'optimal', '0': 'optimal', '3': 'optimal',
                           '2': 'optimal', '4': 'failed: inconsistent OIDs'},
                          self._storage.raid_details())

    def test_reload_remove_readd(self):
        removed_storage = self._storages.pop()

        # configure the RAID to no longer use the removed backend
        self.update_config()
        self._storage.raid_reload()
        self.assertEquals({'1': 'optimal', '0': 'optimal', '3': 'optimal',
                           '2': 'optimal'},
                          self._storage.raid_details())

        # ensure that we can still write to the RAID
        oid = self._storage.new_oid()
        self._dostore(oid=oid)

        # ensure that the transaction did not arrive at the removed backend
        s = removed_storage.open()
        self.assertRaises(ZODB.POSException.POSKeyError, s.load, oid)
        s.close()

        # Re-insert the storage
        self._storages.append(removed_storage)
        self.update_config()
        self._storage.raid_reload()
        self.assertEquals({'1': 'optimal', '0': 'optimal', '3': 'optimal',
                           '2': 'optimal', '4': 'failed: added by controller'},
                          self._storage.raid_details())

        self._storage.raid_recover('4')

        while self._storage.raid_status() != 'optimal':
            time.sleep(0.1)

        self.assertEquals(
            {'1': 'optimal', '0': 'optimal', '3': 'optimal', '2': 'optimal',
             '4': 'optimal'},
            self._storage.raid_details())

        # Now, after recovery, the OID should be visible
        s = removed_storage.open()
        s.load(oid)
        s.close()

    def test_reload_remove_disabled(self):
        removed_storage = self._storages.pop()
        self._storage.raid_disable(removed_storage.name)

        self.assertEquals(
            {'1': 'optimal', '0': 'optimal', '3': 'optimal', '2': 'optimal',
             '4': 'failed: disabled by controller'},
            self._storage.raid_details())

        # configure the RAID to no longer use the removed backend
        self.update_config()

        self._storage.raid_reload()
        self.assertEquals({'1': 'optimal', '0': 'optimal', '3': 'optimal',
                           '2': 'optimal'},
                          self._storage.raid_details())

    def test_reload_broken_config(self):
        self.update_config()
        f = open(self.zeo_configfile, 'w')
        f.write('fdashkjfhdaskkf')
        f.close()

        self.assertRaises(RuntimeError, self._storage.raid_reload)
        self.assertEquals({'1': 'optimal', '0': 'optimal', '3': 'optimal',
                           '2': 'optimal', '4': 'optimal'},
                          self._storage.raid_details())

    def test_reload_no_remaining_storages(self):
        remove = self._storages[:-1]
        self._storages = self._storages[-1:]
        self._storage.raid_disable(self._storages[0].name)

        self.update_config()
        self.assertRaises(RuntimeError, self._storage.raid_reload)
        self.assertEquals({'1': 'optimal', '0': 'optimal', '3': 'optimal',
                           '2': 'optimal',
                           '4': 'failed: disabled by controller'},
                          self._storage.raid_details())


class ClusterModeTests(unittest.TestCase):

    def setUp(self):
        self.raid = gocept.zeoraid.storage.RAIDStorage(
            'test', [Opener('%s' % s) for s in range(5)], fail_mode='close')
        self.raid._apply_storage = mock.Mock(return_value=(True, None))


class ClusterModeCoopTests(ClusterModeTests):

    def setUp(self):
        super(ClusterModeCoopTests, self).setUp()
        self.raid.cluster_mode = 'coop'

    def test_read_operation_chooses_all_storages_op(self):
        self.assert_(
            isinstance(self.raid._reader,
                       gocept.zeoraid.storage.AllStoragesOperation))

    def test_degrade_fails_with_too_few_active_storages(self):
        self.raid._degrade_storage('0', 'test')
        self.raid._degrade_storage('1', 'test')
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          lambda: self.raid._degrade_storage('2', 'test'))
        self.assertTrue(self.raid.closed)

    def test_degrade_turns_readonly(self):
        self.raid.fail_mode = 'read-only'
        self.raid._degrade_storage('0', 'test')
        self.raid._degrade_storage('1', 'test')
        self.assertRaises(ZODB.POSException.ReadOnlyError,
                          lambda: self.raid._degrade_storage('2', 'test'))
        self.assert_(self.raid.isReadOnly())
        self.assertFalse(self.raid.closed)

class ClusterModeSingleTests(ClusterModeTests):

    def setUp(self):
        super(ClusterModeSingleTests, self).setUp()
        self.raid.cluster_mode = 'single'

    def test_read_operation_chooses_single_storage_op(self):
        self.assert_(
            isinstance(self.raid._reader,
                       gocept.zeoraid.storage.SingleStorageOperation))

    def test_degrade_fails_with_no_active_storage(self):
        self.raid._degrade_storage('0', 'test')
        self.raid._degrade_storage('1', 'test')
        self.raid._degrade_storage('2', 'test')
        self.raid._degrade_storage('3', 'test')
        self.assertRaises(ZEO.Exceptions.ClientStorageError,
                          lambda: self.raid._degrade_storage('4', 'test'))

class AllStorageConsistencyCheck(unittest.TestCase):

    def setUp(self):
        self.raid = mock.Mock()
        self.op = gocept.zeoraid.storage.AllStoragesOperation(self.raid)

    def test_equal_results_should_be_consistent(self):
        self.assert_(self.op._extract_result(
            {'1': mock.sentinel.result,
             '2': mock.sentinel.result}))
        self.assertEquals(0, self.raid._degrade_storage.call_count)

    def test_two_different_out_of_two_results_should_be_inconsistent(self):
        self.op._extract_result(
            {'1': mock.sentinel.result1,
             '2': mock.sentinel.result2})
        self.assert_([(('1', 'inconsistent result'), {}),
                      (('2', 'inconsistent result'), {})],
                     self.raid._degrade_storage.call_args_list)

    def test_one_different_out_of_three_results_should_be_consistent(self):
        self.assertEquals(mock.sentinel.result2,
                          self.op._extract_result(
                              {'1': mock.sentinel.result1,
                               '2': mock.sentinel.result2,
                               '3': mock.sentinel.result2}))
        self.raid._degrade_storage.assert_called_with('1', 'inconsistent result')

    def test_three_different_out_of_three_results_should_be_inconsistent(self):
        self.op._extract_result(
            {'1': mock.sentinel.result1,
             '2': mock.sentinel.result2,
             '3': mock.sentinel.result3})
        # We only expect two degrades to happen as we do select one of the
        # results as "good" and rely on the actual implementation of
        # _degrade_storage to raise an exception in that case.
        self.assertEquals(2, self.raid._degrade_storage.call_count)

    def test_extract_non_hashable_result_works(self):
        non_hashable = [1, 2, 3]
        self.assertEquals(non_hashable,
                  self.op._extract_result({'1': non_hashable}))


class OperationExceptionResultTests(unittest.TestCase):

    def result(self, exception):
        return gocept.zeoraid.storage.OperationExceptionResult(exception)

    def test_same_exception_type_and_dict_are_equal(self):
        self.assertEquals(self.result(RuntimeError('foo')),
                          self.result(RuntimeError('foo')))

    def test_unpickleable_exceptions_are_not_equal(self):
        class UnpickleableException(object):
            __slots__ = ()
        self.assertNotEqual(self.result(UnpickleableException()),
                            self.result(UnpickleableException()))

    def test_same_exception_type_and_different_dict_are_not_equal(self):
        self.assertNotEqual(self.result(RuntimeError('foo')),
                            self.result(RuntimeError('bar')))

    def test_different_exception_type_and_same_dict_are_not_equal(self):
        self.assertNotEqual(self.result(RuntimeError('foo')),
                            self.result(TypeError('foo')))

    def test_different_exception_type_and_different_dict_are_not_equal(self):
        self.assertNotEqual(self.result(RuntimeError('foo')),
                            self.result(TypeError('bar')))

    def test_call_should_raise(self):
        exception = RuntimeError('foo')
        try:
            self.result(exception)()
        except RuntimeError, e:
            self.assertEquals(exception, e)
        else:
            self.fail('No exception raised')


class ConfigTests(unittest.TestCase):

    @mock.patch('gocept.zeoraid.storage.RAIDStorage')
    def test_raid_storage_schema(self, raid_class):
        config, handle = ZConfig.loadConfigFile(
            ZODB.config.getStorageSchema(),
            StringIO.StringIO('''\
%import gocept.zeoraid
<raidstorage 1>
    cluster-mode single
    fail-mode read-only
    <mappingstorage 1>
    </mappingstorage>
</raidstorage>
'''))
        self.assertEqual('single', config.storage.config.cluster_mode)
        self.assertEqual('read-only', config.storage.config.fail_mode)

        raid = config.storage.open()
        args, kwargs= raid_class.call_args
        self.assertEqual('1', args[0])
        self.assertEqual('read-only', kwargs['fail_mode'])
        self.assertEqual('single', kwargs['cluster_mode'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZEOReplicationStorageTests, "check"))
    suite.addTest(unittest.makeSuite(FailingStorageSingleTests))
    suite.addTest(unittest.makeSuite(FailingStorageSingleSharedBlobTests))
    suite.addTest(unittest.makeSuite(FailingStorageCoopTests))
    suite.addTest(unittest.makeSuite(FailingStorageCoopSharedBlobTests))
    suite.addTest(unittest.makeSuite(LoggingStorageDistributedTests))
    suite.addTest(unittest.makeSuite(ExtensionMethodsTests))
    suite.addTest(unittest.makeSuite(ClusterModeSingleTests))
    suite.addTest(unittest.makeSuite(ClusterModeCoopTests))
    suite.addTest(unittest.makeSuite(AllStorageConsistencyCheck))
    suite.addTest(unittest.makeSuite(OperationExceptionResultTests))
    suite.addTest(unittest.makeSuite(ConfigTests))
    return suite
