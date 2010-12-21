# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, thread, cPickle as pickle

from threading import Thread
from Queue import Queue, Empty

try:
    from bsddb3 import db as bdb
except ImportError, e:
    from bsddb import db as bdb

from shutil import rmtree, copytree

BTREE = bdb.DB_BTREE
HASH = bdb.DB_HASH

class TransactionExpired(Exception): pass
class FailedIteration(Exception): pass

# A transaction decorator for BDB (from rdflib)
def transaction(f, name=None, **kwds):
    def wrapped(*args, **kwargs):
        index_db = args[0].db
        retries = 10
        delay = 1
        e = None
        
        #t = kwargs['env'].txn_begin()
        while retries > 0:
            (kwargs['txn'], state) = index_db.atomic_begin()

            try:
                result = f(*args, **kwargs)
                index_db.atomic_commit()
                # returns here when the transaction was successful
                return result
            except MemoryError, e:
                # Locks are leaking in this code or in BDB
                # print "out of locks: ", e, sys.exc_info()[0], self.db_env.lock_stat()['nlocks']
                index_db.atomic_rollback()
                retries = 0
            except bdb.DBLockDeadlockError, e:
                #print "Deadlock when adding data: ", e
                index_db.atomic_rollback()
                #sleep(0.1*delay)
                #delay = delay << 1
                retries -= 1
#            except bdb.DBRunRecoveryError, e:
#                print "DBRunRecoveryError", e
#                raise
            # this is raised when the generator is supposed to finish, 
            # and should be re-raised to indicate that the generator is done
            # its also called on garbage collection (ensured by the decorated
            # methods)
            except StopIteration, e:
                raise StopIteration
            
            except FailedIteration, e:
                # this is raised during an iteration with a cursor when a 
                # deadlock occurred. The correct solution is to rollback the
                # transaction. Then StopIteration is raised to notify a calling
                # application.
                index_db.atomic_rollback()
                raise StopIteration                
            # if it is a generic exception, assume it comes from the user and
            # not from BerkeleyDB, abort transaction and forward to the caller.
            except Exception, e:
#                import traceback
#                traceback.print_exc()
                index_db.atomic_rollback()
                raise
                                
        #print "Retries failed!", bdb.db_env.lock_stat()['nlocks']
        raise TransactionExpired("Add failed after exception:" % str(e))

#        except Exception, e:
#            print "Got exception: ", e            
#            bdb.rollback()
            
            #t.abort()

    wrapped.__doc__ = f.__doc__
    return wrapped

class Index(object):
    def __init__(self, name, db, index_type=BTREE, sep='^'):
        self.__name = name
        self.db = db
        self.__db_env = db.db_env
        self.__index_type = index_type
        
        self.__index = bdb.DB(self.__db_env)
        
        # flags necessary to open a free-threaded index with support for
        # transactions.
        # See: http://www.oracle.com/technology/documentation/berkeley-db/db/ref/transapp/data_open.html
#        if self.db.fast_txn:
#            flags = bdb.DB_CREATE | bdb.DB_THREAD
#        else:
        flags = bdb.DB_CREATE | bdb.DB_AUTO_COMMIT | bdb.DB_THREAD

        self.__index.open(self.__name, None, self.__index_type, flags)
        self.__sep = sep

    def __setitem__(self, key, value):
        @transaction
        def setitem(self, key, value, txn=None):
            self.__index.put(key, value, txn=txn)

        try:
            setitem(self, key, pickle.dumps(value))
        except Exception, e:
            raise e

    def __getitem__(self, key):
        @transaction
        def getitem(self, key, txn=None):
            val = self.__index.get(key, txn=txn)
            if val == None or pickle.loads(val) == None:
                raise KeyError(key)
           
            return pickle.loads(val)
 
        try:
            return getitem(self, key)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise e

    def __delitem__(self, key):
        """Removes the key from the hash table."""
        
        @transaction
        def delitem(self, key, txn=None):
            self.__index.delete(key, txn=txn)
            
        try:
            return delitem(self, key)
        except Exception, e:
            raise e

# TODO: contains

    def __iter__(self):
        @transaction
        def _iter(self, txn):
            cursor = self.__index.cursor(txn=txn)
            current = cursor.first() # set_range(prefix)

            while current:
                try:
                    key, value = current

                    if key:                
                        yield (key, pickle.loads(value))
                        current = cursor.next()
                        #print "next: ", current
                    else:
                        current = None
                # this exception is raised when the user does generator.close()
                except GeneratorExit, e:
                    cursor.close()
                    raise StopIteration
                except bdb.DBLockDeadlockError, e:
                    cursor.close()
                    raise FailedIteration(e)
                except Exception, e:
                    #print e
                    cursor.close()
                
            
            cursor.close()
            raise StopIteration

        try:
            return _iter(self)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise
        
    def range_query(self, prefix):
        """
        Executes a range query only returning the values starting with prefix.
        The caller can stop the generator at any time by calling close() on
        the instance (see PEP-0342 for details).
        """
        @transaction
        def _range_query(self, prefix, txn):
            cursor = self.__index.cursor(txn=txn)
            current = cursor.set_range(prefix)

            while current:
                try:
                    key, value = current

                    if key and key.startswith(prefix):                
                        yield (key, pickle.loads(value))
                        current = cursor.next()
                        #print "next: ", current
                    else:
                        current = None
                # this exception is raised when the user does generator.close()
                except GeneratorExit, e:
                    cursor.close()
                    raise StopIteration
                except bdb.DBLockDeadlockError, e:
                    cursor.close()
                    raise FailedIteration(e)                    
                except Exception, e:
                    #print e
                    cursor.close()

            cursor.close()
            raise StopIteration

        try:
            return _range_query(self, prefix)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise

    def __len__(self):
        return self.__index.stat()['ndata']
        
    def close(self):
        try:
            self.__index.close()
        except bdb.DBRunRecoveryError, e:
            # this can occur when a second process using the index crashes 
            # without closing it correctly, ignore this since recovery
            # is run on start-up           
            pass

class DB(object):
    """
    A wrapper class for Berkeley DB transaction environments and databases.
    Hides complexity of transaction management and threads.
    """
    
    def __init__(self, db_path, main_thread=False, backup_path=None, checkpoint_interval=600.0, backup_interval=3600.0*24.0, cachesize=2**26, fatal_recovery=False, fast_txn=False):
        """
        Initalize the DB environment.
        
        ``db_path`` - base directory of the environment
        ``main_thread`` - indicates that this thread should perform checkpoints,
                          archival operations and logging. See the Berkeley DB
                          documentation on Transactional Stores for further
                          information.
        ``backup_path`` - Path to where the database should be archived. It is
                          recommended to perform backups to a separate disk or
                          to a network file-system mount. This path is used if
                          fatal recovery needs to be performed. If the value is
                          None, no archives will be created and fatal recovery
                          is not possible.
                            
        ``checkpoint_interval`` - Indicates how often in seconds a checkpoint 
                                  should be performed.
        ``backup_interval`` - Indicates how often in seconds the database
                              backup procedure is executed.
        ``cachesize`` - sets the size in bytes of the in-memory cache.
        ``fatal_recover`` - performs fatal recovery of the database
        ``fast_txn`` - increases performance by doing in memory logging 
                           and auto-removal of disk logs. Disables D in ACID.
        """
        self.__db_path = os.path.abspath(db_path)

        # create the directory if the environment does not exist already        
        if not os.path.exists(self.__db_path):
            os.mkdir(self.__db_path)

        # db open uses relative names for log and data-dir
        rel_data_dir = 'db_data'
        self.__data_dir = os.path.join(self.__db_path, rel_data_dir)
        if not os.path.exists(self.__data_dir):
            os.mkdir(self.__data_dir)

        rel_log_dir = 'db_logs'
        self.__log_dir = os.path.join(self.__db_path, rel_log_dir)
        if not os.path.exists(self.__log_dir):
            os.mkdir(self.__log_dir)
        
        #panic_event = lambda 

        # initialize the environment
        self.db_env = bdb.DBEnv()
        self.db_env.set_cachesize(0, cachesize)
        
        # set the data dir
        # http://www.oracle.com/technology/documentation/berkeley-db/db/api_c/env_set_data_dir.html
        self.db_env.set_data_dir(rel_data_dir)
        
        # set the log dir and logging parameters
        self.db_env.set_lg_dir(rel_log_dir)

        # enable BDB deadlock-detection
        self.db_env.set_lk_detect(bdb.DB_LOCK_MAXLOCKS)
        
        # flags necessary to create a transaction-aware environment.
        # see: http://www.oracle.com/technology/documentation/berkeley-db/db/ref/transapp/env_open.html

        recovery_type = bdb.DB_RECOVER
                
        if fatal_recovery:
            recovery_type = bdb.DB_RECOVER_FATAL
        
        if not main_thread:
            recovery_type = 0x0
                    
        flags = bdb.DB_CREATE | bdb.DB_INIT_MPOOL | bdb.DB_INIT_LOCK | bdb.DB_INIT_TXN | bdb.DB_INIT_LOG | bdb.DB_THREAD | recovery_type

        self.fast_txn = fast_txn
#        if fast_txn:
#            flags |= bdb.DB_LOG_INMEMORY | bdb.DB_LOG_AUTOREMOVE | bdb.DB_TXN_WRITE_NOSYNC
#            flags |= bdb.DB_TXN_WRITE_NOSYNC


        if fast_txn:
            fast_txn_flags = bdb.DB_TXN_WRITE_NOSYNC | bdb.DB_LOG_AUTOREMOVE
            self.db_env.set_flags(fast_txn_flags, True)

#            self.db_env.set_lg_
#            self.db_env.set_lg_max(10)
#            print self.db_env.get_lg_max()
#            print "fewbfew"
#            try:
#                fast_txn_flags = bdb.DB_LOG_INMEMORY
#                self.db_env.set_flags(fast_txn_flags, True)
#                self.db_env.set_lg_bsize(1024)
#            except Exception, e:
#                print e

        try:
            self.db_env.open(db_path, flags)
        except Exception, e:
            print "db env could not be opened:", e
            
        
        self.__txns = {}
        
        self.__main_thread = main_thread
        self.__backups_enabled = False
        
        # setup checkpointing and the hot backup thread
        if self.__main_thread:
            self.__shutdown_q = Queue()
            self.__checkpoint_interval = checkpoint_interval
            self.__checkpoint_t = Thread(target=self._checkpoint)
            self.__checkpoint_t.start()
            
            if backup_path != None:
                self.__backup_path = backup_path
                
                if not os.path.exists(self.__backup_path):
                    os.mkdir(self.__backup_path)
                
                self.__backup_interval = backup_interval
                self.__backup_t = Thread(target=self._hot_backup)
                self.__backup_t.start()
                self.__backups_enabled = True

    def _hot_backup(self):
        def backup():
            try:
                # perform the hot backup procedure as described in:
                # http://www.oracle.com/technology/documentation/berkeley-db/db/ref/transapp/archival.html
                # see the source for the db_hotbackup-utility for more details
                
                # 1. checkpoint and remove any uncessary log-files
                # this is to avoid copying extra data
                self.db_env.txn_checkpoint()
                self.db_env.log_archive(bdb.DB_ARCH_REMOVE)
                
                # 2. check existance and rights of the root target directory
                if not os.path.exists(self.__backup_path):
                    raise Exception('Could not perform backup since the target directory does not exist, %s' % self.__backup_path)
                
                backup_dir = os.path.join(self.__backup_path, 'db_backup')

                # 3. clean the target directory, assume that the existing data 
                #    has been secured through other means.
                if os.path.exists(backup_dir):
                    rmtree(backup_dir)
                    # recreate the backup-dir since remove_dirs removes it...
                    os.mkdir(backup_dir)
                
                # 4. Copy the data dir to the target dir
                backup_data_dir = os.path.join(backup_dir, os.path.basename(self.__data_dir))
                copytree(self.__data_dir, backup_data_dir)
                
                # 5. Copy the log-dir
                backup_log_dir = os.path.join(backup_dir, os.path.basename(self.__log_dir))
                copytree(self.__log_dir, backup_log_dir)
                

                # 6. perform a fatal recovery on the backup to ensure that
                #    it is valid 
                
                test_env = bdb.DBEnv()
                test_env.set_lg_dir(os.path.basename(backup_log_dir))
                test_env.set_data_dir(os.path.basename(backup_data_dir))
                test_env.set_lk_detect(bdb.DB_LOCK_MAXLOCKS)
                
                recovery_type = bdb.DB_RECOVER_FATAL
                flags = bdb.DB_CREATE | bdb.DB_INIT_MPOOL | bdb.DB_INIT_LOCK | bdb.DB_THREAD | bdb.DB_INIT_LOG | bdb.DB_INIT_TXN | recovery_type
                test_env.open(backup_dir, flags)                
                test_env.close()
                
            except Exception, e:
                print 'hot backup failed: ', e
                
        while True:
            try:
                value = self.__shutdown_q.get(timeout=self.__backup_interval)
                return
            except Empty, e:
                backup()

    def _checkpoint(self):
        while True:
            try:
                value = self.__shutdown_q.get(timeout=self.__checkpoint_interval)
                # if shutdown queue gets a value, finish the thread
                return
            except Empty, e:
                # this can only fail due to arguments
                # http://www.oracle.com/technology/documentation/berkeley-db/db/api_c/txn_checkpoint.html
                self.db_env.txn_checkpoint()
                
    def atomic_begin(self):
        """
        All db calls made within an atomic block is executed with the same 
        transaction. Nested calls to atomic_begin returns the active 
        transaction.
        """
        
        active = False
        try:
            self.__txns[thread.get_ident()]
            active = True
        except KeyError:
            self.__txns[thread.get_ident()] = self.db_env.txn_begin()
        
        return (self.__txns[thread.get_ident()], active)

    def atomic_rollback(self):
        try:
            txn = self.__txns[thread.get_ident()]
            txn.abort()
            del self.__txns[thread.get_ident()]
            active = False
        except KeyError:
            active = False
        except:
            #txn.abort()
            raise
            
    def atomic_commit(self):
        # ends a currently active atomic block
        try:
            txn = self.__txns[thread.get_ident()]
            txn.commit(0)
            del self.__txns[thread.get_ident()]
            active = False
        except KeyError:
            active = False
        except:
            txn.abort()

    def close(self):
        if self.__main_thread:
            # shutdown the checkpointing and backups, must put two shutdowns
            # here to ensure that both threads finish
            self.__shutdown_q.put(None)
            self.__shutdown_q.put(None)            
            self.__checkpoint_t.join()

            if self.__backups_enabled:
                self.__backup_t.join()        
        try:
            self.db_env.close()
        except bdb.DBRunRecoveryError, e:
            # this can occur when a second process using the index crashes 
            # without closing it correctly, ignore this since recovery
            # is run on start-up
            pass    
                    
