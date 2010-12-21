# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import random, os

from bsddb import db

READ = 1
WRITE = 2
# owner is allowed to both read and write
OWNER = 3

class UserDB(object):
    """
    The user database persistently stores ACLs for keys. An ACL is a list of
    users and rights mapped to a key indicating who and in what ways a user
    can access the key. External usernames are mapped to a local ID to simplify
    management when a user wants to change their external name.
    
    The rights available in the system are:
    - owner (o): allowed both read and write-access. An owner can also transfer
             ownership to another user. Multiple owners are allowed.
    - read  (r): user is allowed to read data stored at the key
    - write (w): user is allowed to write/change the data store with the key              
    """
    
    # can we assign roles?
    
    def __init__(self, db_path, db_env=None):
        """
        Initializes a user DB.
        
        - `db_path`: path to where the persistent user-data is stored.
        - `db_env`: A Berkeley DB database environment instance (`bdb.db.DBEnv`)
                    Allows external modules using BDB to perform atomic 
                    operations together with the user db.
        """
        
        self.__db_path = db_path
        
        # <External ID> -> <Local ID>
        self.__extid_index = None
        # <Local ID> -> <External ID>
        self.__lid_index = None
        # <<Local ID> + <Key>> -> <rigths>
        self.__acl_lid_index = None
        # <<Key> + <Local ID>> -> <rigths>
        self.__acl_key_index = None

        # when db_env is defined, there is already a directory where the data
        # is stored                
        if db_env == None and not os.path.exists(db_path):
            os.mkdir(db_path)

        self.__init_db(db_path, db_env)

        self.__sep = '|'
        
    def __init_db(self, db_path, db_env):
        # set the initial cache size, 64MB
        self.__db_env = db_env
        self.__ext_db_env = False
        
        if not self.__db_env:
            self.__db_env = db.DBEnv()

            self.__db_env.set_cachesize(0, 2**26)
        
            flags = db.DB_CREATE | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_INIT_LOG | db.DB_INIT_TXN
            self.__db_env.open(db_path, flags)
        else:
            self.__ext_db_env = True
            
        # <External ID> -> <Local ID>
        self.__extid_index = db.DB(self.__db_env)        
        self.__extid_index.open("extid_lid.db", None, db.DB_HASH, db.DB_CREATE | db.DB_AUTO_COMMIT)

        # <Local ID> -> <External ID>
        self.__lid_index = db.DB(self.__db_env)
        self.__lid_index.open("lid_extid.db", None, db.DB_RECNO, db.DB_CREATE | db.DB_AUTO_COMMIT)

        # <<Local ID> + <Key>> -> <rigths>
        self.__acl_lid_index = db.DB(self.__db_env)
        self.__acl_lid_index.open("acl_lid.db", None, db.DB_BTREE, db.DB_CREATE | db.DB_AUTO_COMMIT)

        # <<Key> + <Local ID>> -> <rigths>
        self.__acl_key_index = db.DB(self.__db_env)
        self.__acl_key_index.open("acl_key.db", None, db.DB_BTREE, db.DB_CREATE | db.DB_AUTO_COMMIT)

    def create_lid(self, user, txn):
        """Increments the recno, and inserts the new value into the user to 
           localid index. Returns the new localid as a string."""
        lid = "%s" % self.__lid_index.append(user, txn)
        self.__extid_index.put(user, lid)
        return lid
        
    def assign_rights(self, key, user, access_type=READ, txn=None):
        """
        Assigns access rights to a key. As owner, the user is allowed to
        both read and write to the key as well as change owner.
        
        - `key`: the key to which an owner will be assigned.
        - `user`: the user-name of the user
        - `access_type`: defines the access rights allowed to the user
        - `txn`: (Optional), if a txn is given, the operations accessing the
                 db-indexes will be part of the transaction. Otherwise, a new
                 transaction will be created.
        """
        ext_txn = True
        if not txn:
            ext_txn = False
            txn = self.__db_env.txn_begin()

        try:            
            lid = self.__extid_index.get(user)
            
            if not lid:
                # user was not found, create a new local id for the user        
                lid = self.create_lid(user, txn)

            self.__acl_lid_index.put(self.__sep.join([lid, key]), str(access_type), txn=txn)
            self.__acl_key_index.put(self.__sep.join([key, lid]), str(access_type), txn=txn)
            
            if not ext_txn:
                txn.commit(0)
        except:
            if ext_txn:
                raise
            
            txn.abort()
            # TODO: improve error handling
            raise
    
    def remove(self, key, txn=None):
        """
        Remove a key from the index.
        
        - `key`: key to remove
        - `txn`: (Optional), if a txn is given, the operations accessing the
                 db-indexes will be part of the transaction. Otherwise, a new
                 transaction will be created.
        """
        ext_txn = True
        if not txn:
            ext_txn = False
            txn = self.__db_env.txn_begin()

        cursor = self.__acl_key_index.cursor(txn=txn)
        current = cursor.set_range(key)

        try:
            # use a cursor to remove all keys, while registering reverse keys
            while current:
                try:
                    key_lid, value = current
                    
                    curr_key, curr_lid = tuple(key_lid.split(self.__sep))

                    if curr_key != key:
                        current = None
                    else:
                        cursor.delete()
                        self.__acl_lid_index.delete(self.__sep.join([curr_lid, curr_key]), txn=txn)
                        current = cursor.next()
                except:
                    cursor.close()
                    if not ext_txn:
                        txn.abort()
                    raise

            cursor.close()
            
            #self.__acl_lid_index.remove(self.__sep.join([lid, key]), str(access_type), txn=txn)
            #self.__acl_key_index.put(self.__sep.join([key, lid]), str(access_type), txn=txn)

            if not ext_txn:
                txn.commit(0)
        except:
            if ext_txn:
                raise
            
            txn.abort()
            raise
                                    
    def is_authorized(self, key, user, access_type=READ, txn=None):
        """
        Checks if the user is authorized to perform the access method on the 
        key. This can also be used to check if a user is the key-owner by 
        defining `access_type` to `benri.userdb.OWNER`.

        - `key`: key for which the user's rights will be checked
        - `user`: the user-name of the user
        - `access_type`: indicates the type of access, defaults to Read.
        - `txn`: (Optional), if a txn is given, the operations accessing the
                 db-indexes will be part of the transaction. Otherwise, a new
                 transaction will be created.
        """
        ext_txn = True
        if not txn:
            ext_txn = False
            txn = self.__db_env.txn_begin()

        try:
            lid = self.__extid_index.get(user)
                        
            if not lid:
                if not ext_txn:
                    txn.abort()
                return False
            
            rights = int(self.__acl_lid_index.get(self.__sep.join([lid, key])))
                
            if (rights & access_type):
                if not ext_txn:
                    txn.commit(0)
                return True

            if not ext_txn:
                txn.abort()
            return False
        except:
            if ext_txn:
                raise
            
            txn.abort()
            raise

    def user_keys(self, user):
        pass

    def close(self):
        self.__extid_index.close()
        self.__lid_index.close()
        self.__acl_lid_index.close()
        self.__acl_key_index.close()
        
        if not self.__ext_db_env:
            self.__db_env.close()

