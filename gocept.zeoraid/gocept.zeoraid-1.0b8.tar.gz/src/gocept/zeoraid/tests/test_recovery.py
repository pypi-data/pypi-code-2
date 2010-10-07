##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
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
"""Test harness for online recovery."""

import itertools
import os
import unittest
import tempfile
import threading
import time
import shutil

import transaction
import ZODB.FileStorage
import ZODB.blob
import ZODB.utils
import ZODB.tests.MinPO
import ZODB.tests.StorageTestBase
import ZODB.POSException

import gocept.zeoraid.recovery


class Opener(object):

    def __init__(self, name, open):
        self.name = name
        self.open = open


def compare(test, source, target):
    recovery = gocept.zeoraid.recovery.Recovery(
        source, target, lambda target: None)
    protocol = list(recovery())
    test.assertEquals([('verified', ''), ('recovered', '')], protocol[-2:])
    for source_txn, target_txn in itertools.izip(source.iterator(),
                                                 target.iterator()):
        # We need not compare the transaction metadata because that has
        # already been done by the recovery's verification run.
        source_records = list(source_txn)
        target_records = list(target_txn)
        test.assertEquals(len(source_records), len(target_records))
        for source_record, target_record in zip(source_records,
                                                target_records):
            for name in 'oid', 'tid', 'data', 'version', 'data_txn':
                test.assertEquals(getattr(source_record, name),
                                  getattr(target_record, name))

            # Check that the loadBefores return the same information
            test.assertEquals(
                source.loadBefore(source_record.oid, source_record.tid),
                target.loadBefore(target_record.oid, target_record.tid))

            if not hasattr(source, 'loadBlob'):
                continue
            try:
                source_file_name = source.loadBlob(
                    source_record.oid, source_record.tid)
            except ZODB.POSException.POSKeyError:
                test.assertRaises(
                    ZODB.POSException.POSKeyError,
                    target.loadBlob, target_record.oid, target_record.tid)
            except TypeError:
                test.assertRaises(
                    TypeError,
                    target.loadBlob, target_record.oid, target_record.tid)
            else:
                target_file_name = target.loadBlob(
                    target_record.oid, target_record.tid)
                test.assertEquals(open(source_file_name, 'rb').read(),
                                  open(target_file_name, 'rb').read())


class ContinuousStorageIterator(ZODB.tests.StorageTestBase.StorageTestBase):

    def setUp(self):
        self._storage = ZODB.FileStorage.FileStorage(tempfile.mktemp())

    def tearDown(self):
        self._storage.close()
        self._storage.cleanup()

    def test_empty_storage(self):
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals([], list(iterator))

    def test_fixed_storage(self):
        self._dostore()
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals(1, len(list(iterator)))

    def test_early_growing_storage(self):
        t1 = self._dostore()
        t2 = self._dostore()
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals(t1, iterator.next().tid)
        t3 = self._dostore()
        self.assertEquals(t2, iterator.next().tid)
        self.assertEquals(t3, iterator.next().tid)
        self.assertRaises(StopIteration, iterator.next)

    def test_late_growing_storage(self):
        t1 = self._dostore()
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals(t1, iterator.next().tid)
        t2 = self._dostore()
        self.assertEquals(t2, iterator.next().tid)
        self.assertRaises(StopIteration, iterator.next)


class OnlineRecovery(unittest.TestCase):

    use_blobs = False
    shared = False

    def store(self, storages, tid=None, status=' ', user=None,
              description=None, extension={}, oid=None):
        if oid is None:
            oid = storages[0].new_oid()

        try:
            data, base_tid = storages[0].load(oid, '')
        except ZODB.POSException.POSKeyError:
            base_tid = ZODB.utils.z64

        data = ZODB.tests.MinPO.MinPO(7)
        data = ZODB.tests.StorageTestBase.zodb_pickle(data)
        # Begin the transaction
        t = transaction.Transaction()
        if user is not None:
            t.user = user
        if description is not None:
            t.description = description
        for name, value in extension.items():
            t.setExtendedInfo(name, value)
        try:
            for storage in storages:
                storage.tpc_begin(t, tid, status)
                if self.use_blobs:
                    handle, blob_file_name = tempfile.mkstemp()
                    os.close(handle)
                    blob_file = open(blob_file_name, 'wb')
                    blob_file.write('I am a happy blob.')
                    blob_file.close()
                    r1 = storage.storeBlob(
                        oid, base_tid, data, blob_file_name, '', t)
                else:
                    r1 = storage.store(oid, base_tid, data, '', t)
                # Finish the transaction
                r2 = storage.tpc_vote(t)
                tid = ZODB.tests.StorageTestBase.handle_serials(oid, r1, r2)
            for storage in storages:
                storage.tpc_finish(t)
        except:
            for storage in storages:
                storage.tpc_abort(t)
            raise
        return tid, oid

    def compare(self, source, target):
        compare(self, source, target)

    def setUp(self):
        self.temp_paths = []
        source_path = tempfile.mktemp()
        target_path = tempfile.mktemp()
        self.source_opener = Opener(
            'source', lambda: ZODB.FileStorage.FileStorage(source_path))
        self.target_opener = Opener(
            'target', lambda: ZODB.FileStorage.FileStorage(target_path))
        self.source = self.source_opener.open()
        self.target = self.target_opener.open()
        self.recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, lambda target: None)

    def tearDown(self):
        self.source.close()
        self.source.cleanup()
        self.target.close()
        self.target.cleanup()
        for path in self.temp_paths:
            shutil.rmtree(path)

    def setup_raid(self):
        if self.use_blobs:
            blob_dir = tempfile.mkdtemp()
            self.temp_paths.append(blob_dir)
        else:
            blob_dir = None

        return gocept.zeoraid.storage.RAIDStorage(
            'raid',
            [self.source_opener, self.target_opener], cluster_mode='single',
            blob_dir=blob_dir, shared_blob_dir=self.shared)

    def test_verify_both_empty(self):
        self.assertEquals([('verified', ''), ('recovered', '')],
                          list(self.recovery()))

    def test_verify_empty_target(self):
        self.store([self.source])
        recovery = self.recovery()
        self.assertEquals('verified', recovery.next()[0])

    def test_verify_shorter_target(self):
        self.store([self.source, self.target])
        self.store([self.source])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])

    def test_verify_equal_length(self):
        self.store([self.source, self.target])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])

    def test_verify_too_long_target(self):
        self.store([self.source, self.target])
        self.store([self.target])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertRaises(ValueError, recovery.next)

    def test_verify_tid_mismatch(self):
        self.store([self.source])
        self.store([self.target])
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_status_mismatch(self):
        tid, _ = self.store([self.source])
        self.store([self.target], tid=tid, status='p')
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_user_mismatch(self):
        tid, _ = self.store([self.source])
        self.store([self.target], tid=tid, user='Hans')
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_description_mismatch(self):
        tid, _ = self.store([self.source])
        self.store([self.target], tid=tid, description='foo bar')
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_extension_mismatch(self):
        tid, _ = self.store([self.source])
        self.store([self.target], tid=tid, extension=dict(foo=3))
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_recover_already_uptodate(self):
        self.store([self.source, self.target])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])

    def test_recover_simple(self):
        self.store([self.source, self.target])
        _, oid = self.store([self.source])
        self.store([self.source], oid=oid)
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.compare(self.source, self.target)

    def test_recover_growing(self):
        self.store([self.source, self.target])
        self.store([self.source])
        recovery = self.recovery()
        self.store([self.source])
        self.assertEquals('verify', recovery.next()[0])
        self.store([self.source])
        self.assertEquals('verified', recovery.next()[0])
        for i in xrange(10):
            self.store([self.source])
            self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.compare(self.source, self.target)

    def test_recover_finalize_already_uptodate(self):
        self.store([self.source, self.target])
        self.finalized = False

        def finalize(target):
            self.finalized = True

        recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, finalize)()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.assertEquals(True, self.finalized)

    def test_recover_no_commit_during_finalize(self):
        self.store([self.source, self.target])
        self.store([self.source])
        self.got_commit_lock = None

        def try_commit():
            t = transaction.Transaction()
            self.got_commit_lock = False
            self.source.tpc_begin(t)
            self.got_commit_lock = True
            self.source.tpc_abort(t)

        def finalize_check_no_commit(target):
            self.thread = threading.Thread(target=try_commit)
            self.thread.start()
            time.sleep(1)
            self.assertEquals(False, self.got_commit_lock)

        recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, finalize_check_no_commit)()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.thread.join()
        self.assertEquals(True, self.got_commit_lock)
        self.compare(self.source, self.target)

    def test_recover_raid_storage(self):
        self.store([self.source, self.target])
        self.store([self.source])
        self.source.close()
        self.target.close()
        raid = self.setup_raid()
        self.assertEquals('degraded', raid.raid_status())
        raid._join()
        raid.raid_recover('target')
        for i in xrange(10):
            time.sleep(1)
            if raid.raid_status() == 'optimal':
                break
        else:
            self.fail('Timeout while RAID recovers.')
        raid.close()
        self.source = self.source_opener.open()
        self.target = self.target_opener.open()
        self.compare(self.source, self.target)


class OnlineBlobStorageRecovery(OnlineRecovery):

    def setUp(self):
        source_blob_dir = tempfile.mkdtemp()
        self.temp_paths = [source_blob_dir]
        if self.shared:
            target_blob_dir = source_blob_dir
        else:
            target_blob_dir = tempfile.mkdtemp()
            self.temp_paths.append(target_blob_dir)

        source_path = tempfile.mktemp()
        target_path = tempfile.mktemp()

        self.source_opener = Opener('source', lambda:
            ZODB.blob.BlobStorage(source_blob_dir,
                ZODB.FileStorage.FileStorage(source_path)))
        self.target_opener = Opener('target', lambda:
            ZODB.blob.BlobStorage(target_blob_dir,
                ZODB.FileStorage.FileStorage(target_path)))

        self.source = self.source_opener.open()
        self.target = self.target_opener.open()
        self.recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, lambda target: None)


class OnlineBlobRecovery(OnlineBlobStorageRecovery):

    use_blobs = True


class OnlineSharedBlobRecovery(OnlineBlobRecovery):

    shared = True


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContinuousStorageIterator))
    suite.addTest(unittest.makeSuite(OnlineRecovery))
    suite.addTest(unittest.makeSuite(OnlineBlobStorageRecovery))
    suite.addTest(unittest.makeSuite(OnlineBlobRecovery))
    suite.addTest(unittest.makeSuite(OnlineSharedBlobRecovery))
    return suite
