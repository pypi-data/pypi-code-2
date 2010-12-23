# me2.plugs.common/quote.py
#
#

""" manage quotes. """

## me2 imports

from me2.lib.commands import cmnds
from me2.lib.examples import examples
from me2.lib.persist import PlugPersist

## basic imports

import random

## defines

quotes = PlugPersist('quotes.data')

if not quotes.data.index:
    quotes.data.index = 0

def handle_quoteadd(bot, event):
    """ add a quote. """
    quotes.data.index += 1
    quotes.data[quotes.data.index] = event.rest
    quotes.save()
    event.reply("quote %s added" % quotes.data.index)

cmnds.add('quote-add', handle_quoteadd, ['USER', 'GUEST'])
examples.add('quote-add' , 'add a quote to the bot', 'quote-add blablabla')

def handle_quote(bot, event):
    """ get a quote. """
    possible = quotes.data.keys()
    possible.remove('index')
    if possible:
        nr = random.choice(possible)
        event.reply("#%s %s" % (nr, quotes.data[nr]))
    else:
        event.reply("no quotes yet.")

cmnds.add('quote', handle_quote, ['USER', 'GUEST'])
examples.add('quote' , 'get a quote from the bot', 'quote')
