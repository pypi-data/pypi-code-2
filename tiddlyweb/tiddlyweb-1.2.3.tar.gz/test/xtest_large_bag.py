
import sys
sys.path.insert(0, '')
import shutil

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store

from tiddlyweb.filters import parse_for_filters

from tiddlyweb.web.sendtiddlers import send_tiddlers

from time import time

store = None
environ = {}

def setup_module(module):

    global store
    global environ
    if module:
        try:
            shutil.rmtree('store')
        except:
            pass
    environ = {
            'tiddlyweb.config': config,
            'tiddlyweb.type': 'text/plain',
            'tiddlyweb.query': {},
            #'tiddlyweb.filters': parse_for_filters('sort=-modified;limit=0,5')[0],
            #'tiddlyweb.filters': parse_for_filters('limit=0,5')[0],
            'tiddlyweb.filters':[],
            }
    server_store = config['server_store']
    store = Store(server_store[0], server_store[1], environ)
    environ['tiddlyweb.store'] = store

    if module:
        bag = Bag('big')
        store.put(bag)
        for i in xrange(2):
            tiddler = Tiddler('tiddler%s' % i, 'big')
            tiddler.modified = '201010100101%02d' % (i % 60)
            tiddler.text = 'text %s' % i
            store.put(tiddler)

def test_get_tiddler_from_bag():
    start = time()
    bag = store.get(Bag('big'))
    output = '\n'.join('%s\n%s' % (stiddler.title, stiddler.text) for stiddler in store.list_bag_tiddlers(bag))
    finish = time()
    total = finish-start
    print total
    assert total < 5.0

def test_send_tiddlers():
    start = time()
    print 'get bag', time()
    bag = store.get(Bag('big'))
    print 'got bag', time()
    def start_response(status, headers):
        pass
    print 'send_tiddlers bag', time()
    output = '\n'.join(line for line in send_tiddlers(environ, start_response, bag))
    print 'sent_tiddlers bag', time()
    #print output
    print 'size', len(output)
    finish = time()
    total = finish-start
    print total

if __name__ == '__main__':
    module = None
    setup_module(module)
    test_send_tiddlers()
