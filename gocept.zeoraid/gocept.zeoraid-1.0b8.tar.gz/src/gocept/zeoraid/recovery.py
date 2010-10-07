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
"""Online storage recovery."""

import ZODB.POSException
import ZODB.utils
import gocept.zeoraid.storage
import logging
import tempfile
import transaction

logger = logging.getLogger('gocept.zeoraid.recovery')


def continuous_storage_iterator(storage):
    seen = ZODB.utils.z64
    while seen < storage.lastTransaction():
        iterator = storage.iterator(seen)
        if seen > ZODB.utils.z64:
            # We can only get an iterator starting with a given transaction,
            # which we have already seen, so we skip it now.
            iterator.next()
        for txn_info in iterator:
            yield txn_info
        seen = txn_info.tid


class Recovery(object):
    """Online storage recovery.

    Environmental requirements:

    - The source storage must not be packed during recovery.

    - The target storage must not be committed to.

    - The caller is responsible for synchronizing the OID counters because we
      cannot do that atomically.

    """

    def __init__(self, source, target, finalize, recover_blobs=True):
        self.source = source
        self.target = target
        self.finalize = finalize
        if recover_blobs:
            if hasattr(source, 'loadBlob'):
                try:
                    source.loadBlob(ZODB.utils.z64, ZODB.utils.z64)
                except ZODB.POSException.POSKeyError:
                    pass
                except TypeError, e:
                    recover_blobs = False
        self.recover_blobs = recover_blobs

    def __call__(self):
        """Performs recovery."""
        # Verify old transactions that may already be stored in the target
        # storage. When comparing transaction records, ignore storage records
        # in order to avoid transferring too much data.
        source_iter = continuous_storage_iterator(self.source)
        target_iter = self.target.iterator()

        while True:
            try:
                target_txn = target_iter.next()
            except StopIteration:
                break
            try:
                source_txn = source_iter.next()
            except StopIteration:
                # An exhausted source storage would be OK if the target
                # storage is exhausted at the same time. In that case, we will
                # already have left the loop though.
                raise ValueError('The target storage contains already more '
                                 'transactions than the source storage.')

            for name in 'tid', 'status', 'user', 'description', 'extension':
                source_value = getattr(source_txn, name)
                target_value = getattr(target_txn, name)
                if source_value != target_value:
                    raise ValueError(
                        '%r mismatch: %r (source) != %r (target) '
                        'in source transaction %r.' % (
                        name, source_value, target_value, source_txn.tid))

            yield ('verify', ZODB.utils.tid_repr(source_txn.tid))

        yield ('verified', '')

        # Recover from that point on until the target storage has all
        # transactions that exist in the source storage at the time of
        # finalization. Therefore we need to check continuously for new
        # remaining transactions under the commit lock and finalize recovery
        # atomically.
        while True:
            t = transaction.Transaction()
            self.source.tpc_begin(t)
            try:
                try:
                    txn_info = source_iter.next()
                except StopIteration:
                    self.finalize(self.target)
                    break
            finally:
                self.source.tpc_abort(t)

            logger.debug('Recovering transaction %s' %
                    ZODB.utils.tid_repr(txn_info.tid))
            self.target.tpc_begin(txn_info, txn_info.tid, txn_info.status)

            for r in txn_info:
                before = self.source.loadBefore(r.oid, txn_info.tid)
                if before is not None:
                    _, prev_tid, _ = before
                else:
                    prev_tid = None

                if self.recover_blobs:
                    try:
                        blob_file_name = self.source.loadBlob(
                            r.oid, txn_info.tid)
                    except ZODB.POSException.POSKeyError:
                        pass
                    else:
                        handle, temp_file_name = tempfile.mkstemp(
                            dir=self.target.temporaryDirectory())
                        gocept.zeoraid.storage.optimistic_copy(blob_file_name,
                                                               temp_file_name)
                        self.target.storeBlob(
                            r.oid, prev_tid, r.data, temp_file_name, r.version,
                            txn_info)
                        continue

                # XXX Charlie Clark has a database that conflicts so we need
                # to reconsider using store here.
                self.target.store(r.oid, prev_tid, r.data, r.version, txn_info)

            self.target.tpc_vote(txn_info)
            self.target.tpc_finish(txn_info)

            yield ('recover', ZODB.utils.tid_repr(txn_info.tid))

        yield ('recovered', '')
