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
"""Tests for ZEORaid being served via ZEO."""

from ZEO.tests import forker
from ZEO.tests.testZEO import get_port
from ZODB.tests import StorageTestBase
import gocept.zeoraid.testing
import os
import tempfile
import transaction
import ZODB.FileStorage
import time


class ZEOServedTests(StorageTestBase.StorageTestBase):

    def setUp(self):
        self._server_storage_files = []
        self._servers = []
        self._pids = []
        self._storages = []

    def tearDown(self):
        for s in self._storages:
            s.close()
        for server in self._servers:
            forker.shutdown_zeo_server(server)
        for pid in self._pids:
            os.waitpid(pid, 0)
        for file in self._server_storage_files:
            if os.path.exists(file):
                os.unlink(file)

    def test_committing_during_recovery(self):
        # Step 1: Create a ZODB with a good bit of content so that recovery
        # will take a while. Also has to be spread over multiple largeish
        # transactions.
        filename1 = tempfile.mktemp()
        self._server_storage_files.append(filename1)
        storage = ZODB.FileStorage.FileStorage(filename1)
        self._storages.append(storage)
        for txn in range(100):
            t = transaction.Transaction()
            storage.tpc_begin(t)
            for record in range(100):
                storage.store(storage.new_oid(), '\0' * 8, 'fdsafsdafdsa' * 10,
                              '', t)
            storage.tpc_vote(t)
            storage.tpc_finish(t)
        storage.close()
        self._storages.pop()

        # Step 2: Fire up a ZEO server that serves two filestorage: an empty
        # one and the prepared one
        port = get_port()
        zconf = forker.ZEOConfig(('', port))
        self._server_storage_files.append(tempfile.mktemp())
        config = """\
        %%import gocept.zeoraid
        <raidstorage 1>
            cluster-mode single
            <filestorage 1>
            path %s
            </filestorage>
            <filestorage 2>
            path %s
            </filestorage>
        </raidstorage>
        """ % tuple(self._server_storage_files)
        zport, adminaddr, pid, path = forker.start_zeo_server(
            config, zconf, port)
        self._pids.append(pid)
        self._servers.append(adminaddr)

        raid = gocept.zeoraid.testing.ZEOOpener(
            '1', zport, storage='1', min_disconnect_poll=0.5, wait=1,
            wait_timeout=60).open()
        self._storages.append(raid)

        self.assertEquals({'1': 'optimal',
                           '2': 'failed: missing transactions'},
                          raid.raid_details())
        self.assertEquals('degraded', raid.raid_status())

        raid.raid_recover('2')

        # Wait until the storage starts to recover
        status = {'2': ''}
        while 'recover ' not in status['2']:
            status = raid.raid_details()
            time.sleep(0.5)

        # Now, hammer the storage with more transactions with a high chance of
        # triggering the waiting list
        # This test is kinda bad: if it fails it gets stuck.
        for txn in range(100):
            t = transaction.Transaction()
            raid.tpc_begin(t)
            for record in range(100):
                raid.store(raid.new_oid(), '\0' * 8, 'fdsafsdafdsa' * 10,
                           '', t)
            raid.tpc_vote(t)
            raid.tpc_finish(t)

        # Wait for the recovery to finish
        while raid.raid_status() == 'recovering':
            time.sleep(1)

        self.assertEquals('optimal', raid.raid_status())
