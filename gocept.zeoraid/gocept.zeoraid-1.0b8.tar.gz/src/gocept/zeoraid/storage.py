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
"""ZEORaid storage implementation."""

from ZEO.runzeo import ZEOOptions
import ZEO.ClientStorage
import ZEO.interfaces
import ZODB.POSException
import ZODB.blob
import ZODB.interfaces
import ZODB.utils
import cPickle
import gocept.zeoraid.interfaces
import gocept.zeoraid.recovery
import logging
import os
import os.path
import persistent.TimeStamp
import random
import shutil
import tempfile
import threading
import time
import transaction
import transaction.interfaces
import zc.lockfile
import zope.interface

logger = logging.getLogger('gocept.zeoraid')


def ensure_open_storage(method):

    def check_open(self, *args, **kw):
        if self.closed:
            raise gocept.zeoraid.interfaces.RAIDClosedError(
                "Storage has been closed.")
        return method(self, *args, **kw)
    return check_open


def ensure_writable(method):

    @ensure_open_storage
    def check_writable(self, *args, **kw):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        return method(self, *args, **kw)
    return check_writable


class ThreadedApplyStorage(threading.Thread):

    reliable = None
    result = None
    exception = None

    def __init__(self, storage_name, method_name, args, kw,
                 expect_connected, apply_storage):
        super(ThreadedApplyStorage, self).__init__()
        self.storage_name = storage_name
        self.method_name = method_name
        self.args = args
        self.kw = kw
        self.expect_connected = expect_connected
        self._apply_storage = apply_storage

    def run(self):
        try:
            self.reliable, self.result = self._apply_storage(
                self.storage_name, self.method_name, self.args,
                self.kw, self.expect_connected)
        except Exception, e:
            self.exception = e


class RAIDStorage(object):
    """The RAID storage is a drop-in replacement for the client storages that
    are configured.

    It has few but important tasks: multiplex all communication to the
    storages, coordinate the transactions between the storages and alert the
    RAID controller if a storage fails.

    """

    zope.interface.implements(ZODB.interfaces.IStorage,
                              ZODB.interfaces.IBlobStorage,
                              ZODB.interfaces.IStorageUndoable,
                              ZODB.interfaces.IStorageCurrentRecordIteration,
                              ZODB.interfaces.IStorageIteration,
                              ZEO.interfaces.IServeable,
                              )

    blob_fshelper = None

    closed = False
    _transaction = None

    # We store the registered database to be able to re-register storages when
    # we bring them back into the pool of optimal storages.
    _db = None

    # Timeout for threaded/parallel operations on backend storages.
    timeout = 6000

    def __init__(self, name, openers, read_only=False, cluster_mode='coop',
                 blob_dir=None, shared_blob_dir=False, zeo=None,
                 fail_mode='close'):
        self.__name__ = name
        self.read_only = read_only
        self.fail_mode = fail_mode
        self.cluster_mode = cluster_mode
        self.shared_blob_dir = shared_blob_dir
        self.zeo = zeo
        self.storages = {}
        self._threads = set()
        self.storages_optimal = []
        self.storages_degraded = []
        self.degrade_reasons = {}

        # Temporary files and directories that should be removed at the end of
        # the two-phase commit. The list must only be modified while holding
        # the commit lock.
        self.tmp_paths = []

        if blob_dir is not None:
            self.blob_fshelper = ZODB.blob.FilesystemHelper(blob_dir)
            self.blob_fshelper.create()
            self.blob_fshelper.checkSecure()

        # Allocate locks
        # The write lock must be acquired when:
        # a) performing write operations on the backends
        # b) writing _transaction
        self._write_lock = threading.RLock()
        # The commit lock must be acquired when setting _transaction, and
        # released when unsetting _transaction.
        self._commit_lock = threading.Lock()

        # Remember the openers so closed storages can be re-opened as needed.
        self.openers = dict((opener.name, opener) for opener in openers)

        # Do not fail the whole storage while opening storages the first time
        # as we have intermittent states that would never allow a RAID to
        # bootstrap.
        self._fail_after_degrade = False
        for name in self.openers:
            self._open_storage(name)
        self._fail_after_degrade = True

        # Evaluate the consistency of the opened storages. We compare the last
        # known TIDs of all storages. All storages whose TID equals the newest
        # of these TIDs are considered optimal.
        tids = {}
        for name, storage in self.storages.items():
            try:
                tid = storage.lastTransaction()
            except StorageDegraded:
                continue
            tids.setdefault(tid, [])
            tids[tid].append(name)

        if not tids:
            # No storage is working.
            raise gocept.zeoraid.interfaces.RAIDError(
                "Can't start without at least one working storage.")

        # Set up list of optimal storages
        self.storages_optimal = tids.pop(max(tids))

        # Degrade all remaining (non-optimal) storages
        for name in reduce(lambda x, y: x + y, tids.values(), []):
            self._degrade_storage(name, reason='missing transactions')

        # No storage is recovering initially
        self.storage_recovering = None
        self.recovery_status = None

    # IStorage

    def close(self):
        """Close the storage."""
        self._join(5)

        if self.closed:
            # Storage may be closed more than once, e.g. by tear-down methods
            # of tests.
            return
        try:
            try:
                AllStoragesOperation(self, expect_connected=False).close()
            except Exception, e:
                logging.exception('asdf')
                if not zeoraid_exception(e):
                    raise e
        finally:
            self.closed = True
            del self.storages_optimal[:]

        self._join(5)

    def getName(self):
        """The name of the storage."""
        return self.__name__

    def getSize(self):
        """An approximate size of the database, in bytes."""
        try:
            return self._reader.getSize()
        except Exception, e:
            if zeoraid_exception(e):
                return 0
            raise e

    def history(self, oid, version='', size=1):
        """Return a sequence of history information dictionaries."""
        assert version is ''
        return self._reader.history(oid, size)

    def isReadOnly(self):
        """Test whether a storage allows committing new transactions."""
        return self.read_only

    def lastTransaction(self):
        """Return the id of the last committed transaction."""
        # Although this is a read operation we apply it to all storages as a
        # safety belt to ensure consistency.
        return AllStoragesOperation(self).lastTransaction()

    def __len__(self):
        """The approximate number of objects in the storage."""
        try:
            return self._reader.__len__()
        except ZEO.Exceptions.ClientStorageError, e:
            if zeoraid_exception(e):
                return 0
            raise e

    def load(self, oid, version=''):
        """Load data for an object id and version."""
        assert version is ''
        return self._reader.load(oid)

    def loadBefore(self, oid, tid):
        """Load the object data written before a transaction id."""
        return self._reader.loadBefore(oid, tid)

    def loadSerial(self, oid, serial):
        """Load the object record for the give transaction id."""
        return self._reader.loadSerial(oid, serial)

    @ensure_writable
    def new_oid(self):
        """Allocate a new object id."""
        self._write_lock.acquire()
        try:
            return self._new_oid()
        finally:
            self._write_lock.release()

    def _new_oid(self):
        # Not write-lock protected implementation of new_oid
        oids = []
        for storage in self.storages_optimal[:]:
            reliable, oid = self._apply_storage(storage, 'new_oid')
            if reliable:
                oids.append((oid, storage))

        min_oid = sorted(oids)[0][0]
        for oid, storage in oids:
            if oid > min_oid:
                self._degrade_storage(storage, reason='inconsistent OIDs')
        return min_oid

    @ensure_writable
    def pack(self, t, referencesf):
        """Pack the storage."""
        # Packing is an interesting problem when talking to multiple storages,
        # especially when doing it in parallel:
        # As packing might take a long time, you can end up with a couple of
        # storages that are packed and others that are still packing.
        # As soon as one storage is packed, you have to prefer reading from
        # this storage.
        #
        # Here, we rely on the following behaviour:
        # a) always read from the first optimal storage
        # XXX a) isn't true anymore!
        # b) pack beginning with the first optimal storage, working our way
        #    through the list.
        # This is a simplified implementation of a way to prioritize the list
        # of optimal storages.
        self._writer.pack(t, referencesf)

    def registerDB(self, db, limit=None):
        """Register an IStorageDB."""
        # We can safely register all storages here as it will only cause
        # invalidations to be sent out multiple times. Transaction
        # coordination by the StorageServer and set semantics in ZODB's
        # Connection class make this correct and cheap.
        self._db = db
        self._writer.registerDB(db)

    def sortKey(self):
        """Sort key used to order distributed transactions."""
        return id(self)

    @ensure_writable
    def store(self, oid, oldserial, data, version, transaction):
        """Store data for the object id, oid."""
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)
        self._write_lock.acquire()
        try:
            self._writer.store(
                oid, oldserial, data, version, transaction)
            return self._tid
        finally:
            self._write_lock.release()

    def tpc_abort(self, transaction):
        """Abort the two-phase commit."""
        self._write_lock.acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                self._writer.tpc_abort(transaction)
                self._transaction = None
            finally:
                self._tpc_cleanup()
                self._commit_lock.release()
        finally:
            self._write_lock.release()
        self._process_zeo_waiting()

    @ensure_writable
    def tpc_begin(self, transaction, tid=None, status=' '):
        """Begin the two-phase commit process."""
        self._write_lock.acquire()
        try:
            if self._transaction is transaction:
                # It is valid that tpc_begin is called multiple times with
                # the same transaction and is silently ignored.
                return

            # Release and re-acquire to avoid dead-locks. commit_lock is a
            # long-term lock whereas write_lock is a short-term lock. Acquire
            # the long-term lock first.
            self._write_lock.release()
            self._commit_lock.acquire()
            self._write_lock.acquire()

            self._transaction = transaction

            if tid is None:
                # No TID was given, so we create a new one.
                tid = self._new_tid(self.lastTransaction())
            self._tid = tid

            self._writer.tpc_begin(transaction, self._tid, status)
        finally:
            self._write_lock.release()

    def tpc_finish(self, transaction, callback=None):
        """Finish the transaction, making any transaction changes permanent.
        """
        result = None
        self._write_lock.acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                self._writer.tpc_finish(transaction)
                if callback is not None:
                    # This callback is relevant for processing invalidations
                    # at transaction boundaries.
                    # XXX It is somewhat unclear whether this should be done
                    # before or after calling tpc_finish. BaseStorage and
                    # ClientStorage contradict each other and the documentation
                    # is non-existent. We trust ClientStorage here.
                    callback(self._tid)
                result = self._tid
            finally:
                self._transaction = None
                self._tpc_cleanup()
                self._commit_lock.release()
        finally:
            self._write_lock.release()
        self._process_zeo_waiting()
        return result

    def tpc_vote(self, transaction):
        """Provide a storage with an opportunity to veto a transaction."""
        self._write_lock.acquire()
        try:
            if transaction is not self._transaction:
                return
            tpc_vote = AllStoragesOperation(
                self, filter_results=unique_serials).tpc_vote
            tpc_vote(transaction)
        finally:
            self._write_lock.release()

    def supportsVersions(self):
        return False

    def modifiedInVersion(self, oid):
        return ''

    # IBlobStorage

    @ensure_writable
    def storeBlob(self, oid, oldserial, data, blob, version, transaction):
        """Stores data that has a BLOB attached."""
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        def get_blob_data():
            # Client storages expect to be the only ones operating on the blob
            # file. We need to create individual appearances of the original
            # file so that they can move the file to their cache location.
            base_dir = tempfile.mkdtemp(dir=os.path.dirname(blob))
            self.tmp_paths.append(base_dir)
            copies = 0
            while True:
                # We need to create a new directory to make sure that
                # atomicity of file creation is preserved.
                copies += 1
                new_blob = os.path.join(base_dir, '%i.blob' % copies)
                os.link(blob, new_blob)
                yield (oid, oldserial, data, new_blob, version, transaction)

        self._write_lock.acquire()
        try:
            if self.shared_blob_dir:
                op = SingleStorageOperation(self)
                result = op.storeBlob(
                    oid, oldserial, data, blob, version, transaction)
                AllStoragesOperation(self, exclude=(op.storage,),
                                     ignore_noop=True).store(
                    oid, oldserial, data, version, transaction)
            else:
                # The back end storages receive links to the blob file and
                # take care of them appropriately. We have to remove the
                # original link to the blob file ourselves.
                self.tmp_paths.append(blob)
                # We'd like to say _writer here but cannot because of the
                # method signature cleverness applied in AllStoragesOperation
                # in order to consume the generator.
                AllStoragesOperation(self)('storeBlob', get_blob_data)
            return self._tid
        finally:
            self._write_lock.release()

    def loadBlob(self, oid, serial):
        """Return the filename of the Blob data for this OID and serial."""
        # XXX needs some refactoring
        blob_filename = self.blob_fshelper.getBlobFilename(oid, serial)
        if os.path.exists(blob_filename):
            return blob_filename

        if self.shared_blob_dir:
            # We're using a back end shared directory. If the file isn't here,
            # it's not anywhere.
            raise ZODB.POSException.POSKeyError("No blob file", oid, serial)

        reader = self._reader
        reader.filter_results = relative_blob_path
        backend_filename = reader.loadBlob(oid, serial)
        lock_filename = blob_filename + '.lock'
        self.blob_fshelper.createPathForOID(oid)
        try:
            lock = zc.lockfile.LockFile(lock_filename)
        except zc.lockfile.LockError:
            while True:
                time.sleep(0.1)
                try:
                    lock = zc.lockfile.LockFile(lock_filename)
                except zc.lockfile.LockError:
                    pass
                else:
                    # We have the lock. We should be able to get the file now.
                    lock.close()
                    try:
                        os.remove(lock_filename)
                    except OSError:
                        pass
                    break

            if os.path.exists(blob_filename):
                return blob_filename

            return None # XXX see ClientStorage

        try:
            optimistic_copy(backend_filename, blob_filename)
        finally:
            lock.close()
            try:
                os.remove(lock_filename)
            except OSError:
                pass

        return blob_filename

    def openCommittedBlobFile(self, oid, serial, blob=None):
        """Return a file for committed data for the given object id and serial
        """

    def temporaryDirectory(self):
        """Return a directory that should be used for uncommitted blob data.
        """
        return self.blob_fshelper.temp_dir

    # IStorageUndoable

    def supportsUndo(self):
        """Return True, indicating that the storage supports undo.
        """
        return True

    @ensure_writable
    def undo(self, transaction_id, transaction):
        """Undo a transaction identified by id."""
        self._write_lock.acquire()
        try:
            return self._writer.undo(transaction_id, transaction)
        finally:
            self._write_lock.release()

    def undoLog(self, first=0, last=-20, filter=None):
        """Return a sequence of descriptions for undoable transactions."""
        return self._reader.undoLog(first, last, filter)

    def undoInfo(self, first=0, last=-20, specification=None):
        """Return a sequence of descriptions for undoable transactions."""
        return self._reader.undoInfo(first, last, specification)

    # IStorageCurrentRecordIteration

    def record_iternext(self, next=None):
        """Iterate over the records in a storage."""
        return self._reader.record_iternext(next)

    # IStorageIteration

    def iterator(self, start=None, stop=None):
        """Return an IStorageTransactionInformation iterator."""
        # XXX This should really include fail-over for iterators over storages
        # that degrade or recover while this iterator is running.
        # XXX This is also a threat to consistency when running in cooperation
        # with other RAID servers.
        return SingleStorageOperation(self).iterator(start, stop)

    # IServeable

    # Note: We opt to not implement lastInvalidations until ClientStorage does.
    # def lastInvalidations(self, size):
    #    """Get recent transaction invalidations."""
    #    return self._reader.lastInvalidations(size)

    def tpc_transaction(self):
        """The current transaction being committed."""
        return self._transaction

    def getTid(self, oid):
        """The last transaction to change an object."""
        return self._reader.getTid(oid)

    def getExtensionMethods(self):
        # This method isn't officially part of the interface but
        # it is supported.
        methods = dict.fromkeys(
            ['raid_recover', 'raid_status', 'raid_disable', 'raid_details',
            'raid_reload'])
        return methods

    # IRAIDStorage

    def raid_status(self):
        if self.storage_recovering:
            return 'recovering'
        if not self.storages_degraded:
            return 'optimal'
        if not self.storages_optimal:
            return 'failed'
        return 'degraded'

    @ensure_open_storage
    def raid_details(self):
        storages = {}
        for storage in self.storages_optimal:
            storages[storage] = 'optimal'
        for storage in self.storages_degraded:
            storages[storage] = 'failed: %s' % (
                self.degrade_reasons.get(storage, 'n/a'))
        if self.storage_recovering:
            msg = 'recovering: '
            if self.recovery_status:
                msg += '%s transaction %s' % self.recovery_status
            else:
                msg += '???'
            storages[self.storage_recovering] = msg
        return storages

    @ensure_open_storage
    def raid_disable(self, name):
        try:
            self._degrade_storage(name, reason='disabled by controller')
        except ZEO.Exceptions.ClientStorageError:
            pass
        return 'disabled %r' % (name,)

    @ensure_open_storage
    def raid_recover(self, name, sync=False):
        self._write_lock.acquire()
        try:
            if self.storage_recovering is not None:
                return
            if name not in self.storages_degraded:
                return

            self.storages_degraded.remove(name)
            del self.degrade_reasons[name]
            self.storage_recovering = name
        finally:
            self._write_lock.release()

        if sync:
            self._recover_impl(name)
        else:
            t = threading.Thread(target=self._recover_impl, args=(name,))
            self._threads.add(t)
            t.setDaemon(True)
            t.start()

        return 'recovering %r' % (name,)

    @ensure_open_storage
    def raid_reload(self):
        if not self.zeo:
            raise RuntimeError(
                'Cannot reload config without running inside ZEO.')

        options = ZEOOptions()
        try:
            options.realize(['-C', self.zeo.options.configfile])
        except Exception, e:
            raise RuntimeError(
                'Could not reload configuration file: '
                'please check your configuration.')

        for candidate in options.storages:
            if candidate.name == self.__name__:
                storage = candidate
                break
        else:
            raise RuntimeError(
                'No storage section found for RAID %s.' % self.__name__)
        configured_storages = dict(
            (opt.name, opt) for opt in storage.config.storages)

        configured_names = set(configured_storages.keys())
        current_names = set(self.openers.keys())

        added = configured_names - current_names
        removed = current_names - configured_names

        # Check whether we would remove all optimal storages. If that's so,
        # then we do not perform the reconfiguration.
        remaining_optimal = set(self.storages_optimal) - removed
        if not remaining_optimal:
            raise RuntimeError(
                'Cannot perform reconfiguration: '
                'all optimal storages would be removed.')

        for name in added:
            self.openers[name] = configured_storages[name]
            self.storages_degraded.append(name)
            self.degrade_reasons[name] = 'added by controller'

        for name in removed:
            self._close_storage(name)
            del self.openers[name]
            if name in self.storages_degraded:
                self.storages_degraded.remove(name)
            if name in self.degrade_reasons:
                del self.degrade_reasons[name]

    # internal

    def _open_storage(self, name):
        assert name not in self.storages, "Storage %s already opened" % name
        storage = None
        try:
            storage = self.openers[name].open()
            assert hasattr(storage, 'supportsUndo') and storage.supportsUndo()
            storage.load('\x00' * 8)
        except ZODB.POSException.POSKeyError, e:
            pass
        except Exception, e:
            logger.exception('Could not open storage %s' % name)
            # We were trying to open a storage. Even if we fail we can't be
            # more broke than before, so don't ever fail due to this.
            self._degrade_storage(
                name, reason='an error occured opening the storage')
            if storage is not None:
                try:
                    storage.close()
                except:
                    pass
            return
        self.storages[name] = storage

    def _close_storage(self, name):
        if name in self.storages_optimal:
            self.storages_optimal.remove(name)
        if name in self.storages:
            storage = self.storages.pop(name)
            t = threading.Thread(target=storage.close)
            self._threads.add(t)
            t.setDaemon(True)
            t.start()

    def _degrade_storage(self, name, reason):
        self._close_storage(name)
        self.storages_degraded.append(name)
        self.degrade_reasons[name] = reason
        logger.critical('RAID %r degraded due to failure of back-end %r. '
                        'Reason: %s' % (self.__name__, name, reason))
        if not self._fail_after_degrade:
            return
        fail = False
        if self.cluster_mode == 'single':
            if not self.storages_optimal:
                fail = 'No storages remain optimal'
        elif self.cluster_mode == 'coop':
            if len(self.storages_optimal) <= len(self.openers) * 0.5:
                fail = 'Less than 50% of the configured storages remain optimal.'
        if fail:
            if self.fail_mode == 'close':
                self.close()
                raise gocept.zeoraid.interfaces.RAIDClosedError(fail)
            elif self.fail_mode == 'read-only':
                self.read_only = True
                raise ZODB.POSException.ReadOnlyError(fail)

    def _apply_storage(self, storage_name, method_name, args=(), kw={},
                        expect_connected=True):
        """Calls a method on a given backend storage.

        Returns a tuple (reliable, result).

        All exceptions raised by this method indicate a user error. Storage
        failure is signalled by declaring the result unreliable.

        """
        # XXX storage might be degraded by now, need to check.
        storage = self.storages[storage_name]
        method = getattr(storage, method_name)
        reliable = True
        result = None
        try:
            result = method(*args, **kw)
        except ZODB.POSException.StorageError:
            # Handle StorageErrors first, otherwise they would be swallowed
            # when POSErrors are handled.
            logger.exception('Error calling %r' % method_name)
            reason = 'an error occured calling %r' % method_name
            reliable = False
        except (ZODB.POSException.POSError,
                transaction.interfaces.TransactionError), e:
            # These exceptions are valid answers from the storage. They don't
            # indicate storage failure.
            raise
        except Exception:
            logger.exception('Error calling %r' % method_name)
            reason = 'an error occured calling %r' % method_name
            reliable = False

        if (isinstance(storage, ZEO.ClientStorage.ClientStorage) and
            expect_connected and not storage.is_connected()):
            reliable = False
            reason = 'storage is not connected'

        if not reliable:
            self._degrade_storage(storage_name, reason=reason)
        return (reliable, result)

    @property
    def _reader(self):
        """Calls the given method on the back-end storages with a strategy
        appropriate for reading.

        """
        if self.cluster_mode == 'single':
            # When run as a single server, we can choose to optimise read
            # operations.
            return SingleStorageOperation(self)
        else:
            # When run in cooperation with other servers, we need to be
            # prepared for the event that foreign write operations have
            # reached only some of the back-ends. Reading from all back-ends
            # ensures consistency.
            return AllStoragesOperation(self)

    @property
    def _writer(self):
        """Calls the given method on the back-end storages with a strategy
        appropriate for writing.

        """
        return AllStoragesOperation(self)

    def _recover_impl(self, name):
        try:
            target = self.openers[name].open()
        except Exception:
            logger.exception('Error opening storage %s' % name)
            self.storage_recovering = None
            self._degrade_storage(name,
                'An error occurred while opening the storage.')
            raise
        self.storages[name] = target
        recovery = gocept.zeoraid.recovery.Recovery(
            self, target, self._finalize_recovery,
            recover_blobs=(self.blob_fshelper and not self.shared_blob_dir))
        try:
            for msg in recovery():
                self.recovery_status = msg
                logger.debug(str(msg))
        except Exception:
            logger.exception('Error recovering storage %s' % name)
            self.storage_recovering = None
            self._degrade_storage(name,
                'An error occured recovering the storage')
            raise

    def _finalize_recovery(self, storage):
        self._write_lock.acquire()
        try:
            # Synchronize OIDs: check which one is further down giving out
            # OIDs. Due to ZEO allocation massively at once this might also be
            # the recovering storage. Give it exactly one try to catch up. If
            # we miss the target, we simply degrade the recovering storage
            # again.
            max_optimal = self._new_oid()
            max_recovering = self.storages[self.storage_recovering].new_oid()
            if max_optimal != max_recovering:
                if max_optimal > max_recovering:
                    target = max_optimal
                    catch_up = self.storages[self.storage_recovering].new_oid
                else:
                    target = max_recovering
                    catch_up = self._new_oid

                oid = None
                while oid < target:
                    oid = catch_up()

                if oid != target:
                    self._degrade_storage(
                        self.storage_recovering,
                        reason='failed matching OIDs')
                    return

            self.storages_optimal.append(self.storage_recovering)
            self.storage_recovering = None
        finally:
            self._write_lock.release()

    def _new_tid(self, old_tid):
        """Generates a new TID."""
        if old_tid is None:
            old_tid = ZODB.utils.z64
        old_ts = persistent.TimeStamp.TimeStamp(old_tid)
        now = time.time()
        new_ts = persistent.TimeStamp.TimeStamp(
            *(time.gmtime(now)[:5] + (now % 60,)))
        new_ts = new_ts.laterThan(old_ts)
        return repr(new_ts)

    def _tpc_cleanup(self):
        while self.tmp_paths:
            path = self.tmp_paths.pop()
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except OSError:
                pass

    def _process_zeo_waiting(self):
        if not hasattr(self, '_waiting'):
            return
        # XXX This is a hack because ZEO's StorageServer stores private data
        # on us and doesn't expect us to lock/unlock ourselves without it
        # noticing. Due to that it can happen that transactions get blocked
        # but never restarted. We have to implement the restart dance
        # ourselves here. We hope that ZODB will grow a mechanism to do this
        # cleanly in the future.
        #
        # Restart any client waiting for the storage lock.
        while self._waiting:
            delay, zeo_storage = self._waiting.pop(0)
            try:
                zeo_storage._restart(delay)
            except:
                zeo_storage.log(
                    "Unexpected error handling waiting transaction",
                    level=logging.WARNING, exc_info=True)
                zeo_storage.connection.close()
                continue

            if self._waiting:
                n = len(self._waiting)
                zeo_storage.log("Blocked transaction restarted.  "
                         "Clients waiting: %d" % n)
            else:
                zeo_storage.log("Blocked transaction restarted.")

    def _join(self, timeout=None):
        # We give all the threads a chance to get done quickly.
        # This is mostly a convenience for the tests to not annoy.
        for x in self._threads:
            x.join(timeout)


class StorageOperation(object):

    def __init__(self, raid):
        self.raid = raid

    def __getattr__(self, name):
        if name.startswith('_') and name not in ['__len__']:
            raise AttributeError(name)
        return lambda *args, **kw: self(name, args, kw)

    @property
    def closed(self):
        return self.raid.closed


class SingleStorageOperation(StorageOperation):

    name = None

    @ensure_open_storage
    def __call__(self, method_name, args=(), kw={}):
        """Calls the given method on a random optimal storage."""
        # Try to find a storage that we can talk to. Stop after we found a
        # reliable result.
        storages = self.raid.storages_optimal[:]
        while storages:
            name = random.choice(storages)
            storages.remove(name)
            reliable, result = self.raid._apply_storage(
                name, method_name, args, kw)
            if reliable:
                self.storage = name
                return result

        # We could not determine a result from any storage.
        raise gocept.zeoraid.interfaces.RAIDError("RAID storage is failed.")


class AllStoragesOperation(StorageOperation):

    def __init__(self, raid, expect_connected=True, exclude=(),
                 ignore_noop=False, filter_results=lambda x, y: x):
        super(AllStoragesOperation, self).__init__(raid)
        self.expect_connected = expect_connected
        self.exclude = exclude
        self.ignore_noop = ignore_noop
        self.filter_results = filter_results

    @ensure_open_storage
    def __call__(self, method_name, args=(), kw={}):
        """Calls the given method on all optimal backend storages in order.

        `args` can be given as an n-tuple with the positional arguments that
        should be passed to each storage.

        Alternatively `args` can be a callable that returns an iterable. The
        N-th item of the iterable is expected to be a tuple, passed to the
        N-th storage.

        """
        if callable(args):
            argument_iterable = args()
        else:
            # Provide a fallback if `args` is given as a simple tuple.
            static_arguments = args

            def dummy_generator():
                while True:
                    yield static_arguments
            argument_iterable = dummy_generator()

        applicable_storages = self.raid.storages_optimal[:]
        applicable_storages = [storage for storage in applicable_storages
                               if storage not in self.exclude]

        if not applicable_storages:
            if self.ignore_noop:
                return
            raise gocept.zeoraid.interfaces.RAIDError(
                'No applicable storages for operation %s available.' %
                method_name)
        # Run _apply_storage on all applicable storages in parallel.
        threads = []
        for storage_name in applicable_storages:
            args = argument_iterable.next()
            t = ThreadedApplyStorage(
                storage_name, method_name, args, kw,
                self.expect_connected, self.raid._apply_storage)
            threads.append(t)
            t.start()

        # Wait for threads to finish and pick up results.
        results = {}
        for thread in threads:
            # XXX The timeout should be calculated such that the total time
            # spent in this loop doesn't grow with the number of storages.
            thread.join(self.raid.timeout)
            if thread.isAlive():
                # Storage timed out.
                self.raid._degrade_storage(
                    thread.storage_name,
                    reason='no response within %s seconds' %
                        self.raid.timeout)
                self.raid._threads.add(thread)
                continue
            if thread.exception:
                results[thread.storage_name] = OperationExceptionResult(
                    thread.exception)
            elif thread.reliable:
                results[thread.storage_name] = OperationResult(
                    thread.result,
                    self.filter_results(thread.result,
                                        self.raid.storages.get(thread.storage_name)))

        try:
            result = self._extract_result(results)
        except RuntimeError:
            logger.debug(
                'Received inconsistent results for method %s: %r' %
                (method_name, results))
            raise

        return result()

    def _extract_result(self, results):
        """Extract a consistent result from a set of results.

        We select the result that was returned by the most storages and rely
        on the implementation of _degrade_storage to disable the RAID
        completely if too few storages were involved delivering that result.

        We expect _degrade_storage to raise an exception in the latter case.

        """
        result_classes = NonHashingDict()
        # Classify results by their value, keep track of the storages that
        # returned the respective result.
        for storage, result in results.items():
            storages = result_classes.setdefault(result, [])
            storages.append(storage)
        # Select the result that was returned most.
        max_same_result = 0
        for result, storages in result_classes.items():
            if len(storages) > max_same_result:
                max_same_result = len(storages)
                extracted_result = result
        # Degrade all storages with different results.
        for result, storages in result_classes.items():
            if result != extracted_result:
                for storage in storages:
                    self.raid._degrade_storage(storage, 'inconsistent result')
        return extracted_result


def optimistic_copy(source, target):
    """Try creating a hard link to source at target. Fall back to copying the
    file.
    """
    try:
        os.link(source, target)
    except OSError:
        ZODB.blob.copied("Copied blob file %r to %r.", source, target)
        file1 = open(source, 'rb')
        file2 = open(target, 'wb')
        try:
            ZODB.utils.cp(file1, file2)
        finally:
            file1.close()
            file2.close()


def unique_serials(serials, storage):
    """Filter a sequence of oid/serial pairs and remove late duplicates."""
    if serials is None:
        return
    # I keep both a list and a set: the list ensures order, the set ensures
    # containment test performance.
    seen = set()
    result = []
    for pair in serials:
        if pair in result:
            continue
        result.append(pair)
        seen.add(pair)
    return result


def relative_blob_path(path, storage):
    """Normalise a path to a blob by getting rid of the tmp dir part."""
    if path.startswith(storage.fshelper.temp_dir):
        return path.replace(storage.fshelper.temp_dir, 'TMP:', 1)
    if path.startswith(storage.fshelper.base_dir):
        return path.replace(storage.fshelper.base_dir, '', 1)


def zeoraid_exception(e):
    """Determine whether the given exception is a RAID error.

    Unfortunately creating custom exceptions breaks ZEO clients as the
    exceptions might get pickled but ZEORaid code isn't installed on the
    clients.

    We thus default to raising simple exceptions that we annotate with a
    special attribute.

    """
    return bool(getattr(e, 'created_by_zeoraid', False))


class NonHashingDict(object):

    def __init__(self):
        self.data = []

    def setdefault(self, key, default=None):
        for candidate_key, value in self.data:
            if key == candidate_key:
                return value
        self.data.append((key, default))
        return default

    def items(self):
        return self.data[:]


class OperationResult(object):

    def __init__(self, original, filtered):
        self.original = original
        self.filtered = filtered

    def __eq__(self, other):
        if isinstance(other, OperationResult):
            return self.filtered == other.filtered
        return NotImplemented

    def __call__(self):
        return self.original


class OperationExceptionResult(object):

    def __init__(self, exception):
        self.exception = exception

    def __eq__(self, other):
        if not isinstance(other, OperationExceptionResult):
            return NotImplemented
        try:
            return cPickle.dumps(self.exception) == cPickle.dumps(other.exception)
        except cPickle.PicklingError:
            return False

    def __call__(self):
        raise self.exception
