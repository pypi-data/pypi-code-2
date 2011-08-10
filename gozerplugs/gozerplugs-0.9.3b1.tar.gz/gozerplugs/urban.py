# plugs/urban.py
#
#

""" query urbandictionary """

__copyright__ = 'this file is in the public domain'
__author__ = "Bas van Oostveen"

from gozerbot.generic import geturl2
from gozerbot.commands import cmnds
from gozerbot.aliases import aliases
from gozerbot.examples import examples
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

import urllib, json

plughelp.add('urban', 'query urbandictionary.com')

url = "http://www.urbandictionary.com/iphone/search/define?term="

def handle_urban(bot, ievent):
    """ urban <what> .. search urban for <what> """
    if len(ievent.args) > 0:
	what = " ".join(ievent.args)
    else:
        ievent.missing('<search query>')
        return

    try:
	data = geturl2(url + urllib.quote_plus(what))
	if not data:
	    ievent.reply("word not found: %s" % what)
	    return

	data = json.loads(data)
	if data['result_type'] == 'no_results':
	    ievent.reply("word not found: %s" % what)
	    return

	res = []
	for r in data['list']:
	    res.append(r['definition'])
	ievent.reply(res, dot=True) # dot=" | ")
    except:
	raise

cmnds.add('urban', handle_urban, 'USER')
examples.add('urban', 'urban <what> .. search \
urbandictionary for <what>','1) urban bot 2) urban shizzle')


