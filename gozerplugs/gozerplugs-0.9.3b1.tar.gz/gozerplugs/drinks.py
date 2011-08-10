# plugs/drinks.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

import os, string, random
import urllib, urllib2, json, re

plughelp.add('drinks', 'serve coffee/tea')

wikipedia_url = "http://en.wikipedia.org/w/api.php?"
wikipedia_url += "action=query&cmlimit=100&format=json"
wikipedia_url += "&list=categorymembers&cmtitle="

wikipedia_ns_main = '0'
wikipedia_ns_cat = '14'

coffee = []
tea = []

def init():
    global tea

    for tv in wikipedia_fetch('Category:Tea_varieties', wikipedia_ns_cat):
        for t in wikipedia_fetch(tv, wikipedia_ns_main):
            tea.append(t.strip())

    for c in wikipedia_fetch('Category:Coffee_beverages', wikipedia_ns_main):
        coffee.append(c.strip())

def wikipedia_fetch(category, ns):
    members = []

    try:
	args = urllib.quote_plus(category) + '&cmnamespace=' + ns
	response = urllib2.urlopen(wikipedia_url + args)
    except IOError:
	return members

    try:
	result = json.loads(response.read())
    except ValueError:
	return members
    for m in result['query']['categorymembers']:
	if m['title'].startswith('List of'):
	    continue
	title = re.sub("\ \(.*\)$", '', m['title'])
	members.append(title)

    return members

def handle_coffee(bot, ievent):
    """ get a coffee """
    if not coffee:
	return
    rand = random.randint(1,len(coffee))
    bot.action(ievent.channel, 
	"pours %s a cup of %s" % (ievent.nick, coffee[rand-1]))

def handle_tea(bot, ievent):
    """ get a tea """
    if not tea:
	return
    rand = random.randint(1,len(tea))
    bot.action(ievent.channel, 
	"pours %s a cup of %s" % (ievent.nick, tea[rand-1]))
    
cmnds.add('coffee', handle_coffee, 'USER')
examples.add('coffee', 'get a coffee', 'coffee')
tests.add('coffee')

cmnds.add('tea', handle_tea, 'USER')
examples.add('tea', 'get a tea', 'tea')
tests.add('tea')

