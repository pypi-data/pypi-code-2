# plugs/tinyurl.py
#
#

""" tinyurl.com feeder """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'
__depend__ = ['url', ]
__depending__ = ['rss', ]

from gozerbot.aliases import aliases
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.generic import striphtml, useragent, rlog
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.plugins import plugins

import urllib, urllib2, urlparse, re

plughelp.add('tinyurl', 'the tinyurl url provides a tiny url for the url \
provided as argument or the last url in the log')

re_url_match  = re.compile(u'((?:http|https)://\S+)')

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.search(url):
        return False
    parts = urlparse.urlparse(url)
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]:
        cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]:
        cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]:
        cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl

def get_tinyurl(url):
    """ grab a tinyurl """
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urllib.urlencode(postarray)
    req = urllib2.Request(url='http://tinyurl.com/create.php', data=postdata)
    req.add_header('User-agent', useragent())
    try:
        res = urllib2.urlopen(req).readlines()
        #raise Exception("mekker")
    except urllib2.URLError, e:
        rlog(10, 'tinyurl', 'URLError: %s' % str(e))
        return
    except urllib2.HTTPError, e:
        rlog(10, 'tinyurl', 'HTTP error: %s' % str(e))
        return
    urls = []
    for line in res:
        if line.startswith('<blockquote><b>'):
            urls.append(striphtml(line.strip()).split('[Open')[0])
    if len(urls) == 3:
        urls.pop(0)
    return urls

def handle_tinyurl(bot, ievent):
    """ get tinyurl from argument or last url in log """
    url = None

    if ievent.rest:
        url = ievent.rest
    else:
	if plugins['url']:
	    url = plugins['url'].cache.fetch(bot, ievent)

    if not url:
        ievent.missing('<url>')
        return
    if not valid_url(url):
        ievent.reply('invalid or bad URL')
        return

    tinyurl = get_tinyurl(url)
    if tinyurl:
        ievent.reply(' .. '.join(tinyurl))
    else:
        ievent.reply('failed to create tinyurl')

cmnds.add('tinyurl', handle_tinyurl, 'USER', threaded=True)
examples.add('tinyurl', 'show a tinyurl', 'tinyurl http://gozerbot.org')
aliases.data['tu'] = 'tinyurl'
