# plugs/url.py
#
#

__depending__ = ['tinyurl', 'snarf', ]

from gozerbot.generic import handle_exception, rlog, convertpickle
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.datadir import datadir
from gozerbot.persist.persiststate import PlugState
from gozerbot.tests import tests

import re, os

plughelp.add('url', 'maintain searchable logs of urls')
re_url_match  = re.compile(u'((?:http|https)://\S+)')

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'url', \
datadir + os.sep + 'plugs' + os.sep + 'url' + os.sep + 'state') 

class URLcache(object):
    state = None

    def __init__(self):
	self.state = PlugState()
	self.state.define('urls', {})

    def size(self):
	s = 0
	for i in self.state['urls'].values():
	    for j in i.values():
		s += len(j)
	return str(s)

    def add(self, bot, ievent, i):
        if not self.state['urls'].has_key(bot.name):
            self.state['urls'][bot.name] = {}
        if not self.state['urls'][bot.name].has_key(ievent.printto):
            self.state['urls'][bot.name][ievent.printto] = []
        self.state['urls'][bot.name][ievent.printto].append(i)  
	self.state.save()

    def fetch(self, bot, ievent):
	try:
	    return self.state['urls'][bot.name][ievent.printto][-1]
	except KeyError:
	    return

    def search(self, bot, ievent):
	urls = []

	if bot and ievent:
	    try:
		urls = self.state['urls'][bot.name][ievent.printto]
	    except KeyError:
		pass
	return urls


cache = URLcache()

def urlpre(bot, ievent):
    return re_url_match.findall(ievent.txt)

def urlcb(bot, ievent):
    try:
        test_urls = re_url_match.findall(ievent.txt)
        for i in test_urls:
	    cache.add(bot, ievent, i)
    except Exception, ex:
        handle_exception()

callbacks.add('PRIVMSG', urlcb, urlpre, threaded=True)

def handle_urlsearch(bot, ievent):
    if not ievent.rest:
        ievent.missing('<what>')
        return

    result = []
    try:
        for url in cache.search(bot, ievent):
            if ievent.rest in url:
                result.append(url)
    except Exception, ex:
        ievent.reply(str(ex))
        return
    if result:
        ievent.reply('results matching %s: ' % ievent.rest, result, nr=True)
    else:
        ievent.reply('no result found')
        return

cmnds.add('url-search', handle_urlsearch, ['USER', 'WEB', 'CLOUD'])
examples.add('url-search', 'search matching url entries', 'url-search gozerbot')
tests.add('url-search gozerbot')

def size():
    return cache.size()

def handle_urlsize(bot, ievent):
    ievent.reply(cache.size())

cmnds.add('url-size', handle_urlsize, 'OPER')
examples.add('url-size', 'show number of urls in cache', 'url-size')
tests.add('url-size')
