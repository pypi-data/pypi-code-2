"""memorystore.py - Simple thread-safe in-memory key-value datastore

Usage examples

Start by importing memorystore module:

>>> import memorystore

Initiate a new memorystore and get a handler to it:

>>> store = memorystore.get_handler('store01')

Insert/update variable:

>>> store.update('message', 'Hello World!')
True

Read variable

>>> print(store.get('message'))
Hello World!

Switching to a new store is just a matter of getting a new handler

>>> store = memorystore.get_handler('store02')

A store with a different name is of course now empty:

>>> print(store.get('message'))
None

There is also support for store-level transactions. By starting
a store-level transaction, you can be make sure that no other
thread or process is using the same store during the transaction.

Start a transaction by calling:

>>> store.begin()
True

Do updates etc. as required:

>>> print (store.update('message', 'Doing a transaction'))
True

Finalise transaction by calling commit:

>>> store.commit()
True

No support for rollback is available at the moment.

You can also store Python primitives, such as objects, but
they may cause concurrency problems if care is not taken.
"""

import threading

__memorystore_datastores = dict()
__memorystore_writelock = threading.Lock()

class MemoryDatastore:
	""" Memory Datastore Class """
	
	def __init__(self, name):
		"""Init memory datastore"""
		self.name = name
		self.vars = dict() # each var consist of tuple [content, lock]
		self.vlock = threading.Lock()
		
	def get(self, key):
		"""Get data from a key"""
		if not self.vars.has_key(key):
			return None
		return self.vars[key][0]
	
	def update(self, var, content):
		"""Update/insert key with content"""
		if self.vars.has_key(var):
			# Update (using write lock)
			self.vars[var][1].acquire()
			self.vars[var][0]=content
			self.vars[var][1].release()
		else:
			# Insert
			self.vars[var] = [content, threading.Lock()]
		return True
			
	def begin(self):
		"""Start a transaction with store that requires a store-level lock"""
		self.vlock.acquire()
		return True
	
	def commit(self):
		"""Ends (commits) a transaction -- counterpart of begin"""
		self.vlock.release()
		return True

def get_handler(store_name):
	"""Acquire read/write access to a MemoryDatastore.
	   Initiates datastore if it didn't exist before
	   
	   Arguments: store_name - Name of store (will be converted to string)
	   
	   Returns: An instance of MemoryDatastore"""
	__memorystore_writelock.acquire() # Acquire lock to memorydb datastore list
	parsed_store_name = '%s' % store_name
	if not __memorystore_datastores.has_key(parsed_store_name):
		__memorystore_datastores[parsed_store_name] = MemoryDatastore(parsed_store_name)
	store = __memorystore_datastores.get(parsed_store_name)
	__memorystore_writelock.release() # Release lock to memorydb datastore list
	return store

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
