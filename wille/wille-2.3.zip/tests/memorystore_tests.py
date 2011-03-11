import sys; sys.path.append('..')

from wille.memorystore import MemoryDatastore, get_handler

# Isolation tests 
store1 = get_handler('store1')
store2 = get_handler('store2')
store1.update('key','val1')
store2.update('key','val2')
val1 = store1.get('key')
val2 = store2.get('key')
assert( val1=='val1' )
assert( val2=='val2' )
