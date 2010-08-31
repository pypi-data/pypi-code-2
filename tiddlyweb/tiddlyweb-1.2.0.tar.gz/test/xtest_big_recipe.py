import shutil
import time
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlywebplugins.utils import get_store
from tiddlyweb.config import config

from tiddlyweb.control import get_tiddlers_from_recipe
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.model.collections import Tiddlers

def setup_module(module):
    shutil.rmtree('store')
    module.store = get_store(config)
    from tiddlywebwiki import init
    init(config)
    module.environ = {'tiddlyweb.store': store,
            'tiddlyweb.config': config,
            'tiddlyweb.query': {},
            'tiddlyweb.filters': [],
            'tiddlyweb.type': 'text/x-tiddlywiki',
            'REQUEST_METHOD': 'GET',
            }


def test_big():
    for i in range(1, 40):
        bags = []
        recipe = Recipe('recipe%s' % i)
        for j in range(1, i):
            bag = Bag('bag%s' % j)
            store.put(bag)
            bags.append((bag, ''))
            for k in range(1, j):
                tiddler = Tiddler('tiddler%s' % k, bag.name)
                tiddler.text = 'text%s%s%s' % (i, j, k)
                store.put(tiddler)
        recipe.set_recipe(bags)
        store.put(recipe)


    recipe = store.get(Recipe('recipe39'))
    print 'getting tiddlers', time.time()
    tiddlers = get_tiddlers_from_recipe(recipe)

    print 'containing tiddlers', time.time()
    try:
        tiddlercontainer = Tiddlers(store=store)
    except:
        tiddlercontainer = Tiddlers()

    for tiddler in tiddlers:
        tiddler.recipe = recipe.name
        tiddlercontainer.add(tiddler)

    def start_response(status, headers):
        pass

    print 'sending tiddlers', time.time()
    output = send_tiddlers(environ, start_response, tiddlers=tiddlercontainer)
    print 'sent tiddlers', time.time()
    for i in output:
        print i
        print '#####'
