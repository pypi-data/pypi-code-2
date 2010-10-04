"""
Tests to observe generator behavior.
"""

import shutil

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config
from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer

def setup_module(module):
    try:
        shutil.rmtree('store')
    except OSError:
        pass
    server_store = config['server_store']
    module.store = Store(server_store[0], server_store[1], {'tiddlyweb.config': config})
    bag = Bag('foo')
    module.store.put(bag)
    for i in xrange(20):
        i = str(i)
        tiddler = Tiddler(i, 'foo')
        tiddler.text = '%s foo' % i
        module.store.put(tiddler)

def test_watch():
    bag = store.get(Bag('foo'))
    tiddlers = store.list_bag_tiddlers(bag)
    print 'listed the tiddlers'
    serializer = Serializer('text', {'tiddlyweb.config': config})
    for item in serializer.list_tiddlers(tiddlers):
        print item.encode('utf-8'),


