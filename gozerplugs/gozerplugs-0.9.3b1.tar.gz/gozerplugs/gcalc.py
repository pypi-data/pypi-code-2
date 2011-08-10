# plugins/gcalc.py
# encoding: utf-8

__copyright__ = 'This file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
from gozerbot.aliases import aliasset

import urllib, urllib2, json, re

url = "http://www.google.com/ig/calculator?oe=utf-8&q="

plughelp.add('gcalc', 'use the google calculator')

def handle_gcalc(bot, ievent):
    if len(ievent.args) > 0:
        expr = " ".join(ievent.args)
    else:
        ievent.missing('Missing an expression')
        return

    try:
	response = urllib2.urlopen(url + urllib.quote_plus(expr)) 
    except IOError:
	ievent.reply('request failed')
	return

    try:
	data = response.read()
	# keys quotes fixup
	data = re.sub("(['\"])?([a-zA-Z0-9]+)(['\"])?:", '"\\2":', data)
	result = json.loads(data)
    except ValueError:
	ievent.reply('decoding failed')
	return

    if result['error']:
        ievent.reply('request failed: ' + result['error'])
    else:
        ievent.reply("%s = %s" % (result['lhs'], result['rhs']))
    return

cmnds.add('gcalc', handle_gcalc, 'USER')
examples.add('gcalc', 'Calculate an expression using the google calculator', 'gcalc 1 + 1')
aliasset('calc', 'gcalc')

#tests.add('gcalc 1 + 1')
