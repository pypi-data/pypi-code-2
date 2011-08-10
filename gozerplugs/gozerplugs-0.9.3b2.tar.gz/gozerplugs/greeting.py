# plugs/greeting.py
#
#

""" say greet message when user joins """

__copyright__ = 'this file is in the public domain'

from gozerbot.utils.generic import convertpickle
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.persist.pdol import Pdol
from gozerbot.datadir import datadir
from gozerbot.users import users
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

## basic imports

import random
import os
import logging

plughelp.add('greeting', 'the greeting plugin allows users to set messages \
to be said when they join a channel')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'greetings', \
datadir + os.sep + 'plugs' + os.sep + 'greeting' + os.sep + 'greetings')

cfg = PersistConfig()
cfg.define('enable', [])

greetings = None

def init():
    """ init the greeting plugin """
    global greetings
    greetings = Pdol(datadir + os.sep + 'plugs' + os.sep + 'greeting' + \
os.sep + 'greetings')
    if not greetings.data:
        upgrade()
        greetings = Pdol(datadir + os.sep + 'plugs' + os.sep + 'greeting' + \
os.sep + 'greetings')
    return 1

def greetingtest(bot, ievent):
    """ check if greeting callback should be called """
    logging.warn("greeting - checking %s" % ievent.orig)
    try:
        if ievent.time < bot.timejoined[ievent.channel] + 5:
            return 0
    except KeyError:
        return 0
    if greetings and ievent.channel not in cfg.get('enable'):
        return 0
    if ievent.channel not in bot.state['joinedchannels']:
        return 0
    if ievent.fromm == bot.user:
        return 0
    if bot.type == 'xmpp':
        logging.warn(ievent.c)
        if ievent.c == 'http://jabber.org/protocol/caps':
            return 0
        if  ievent.type == "available":
            return 1
    else:
        return 1
    return 0

def greetingcallback(bot, ievent):
    """ do the greeting """
    #username = users.getname(ievent.userhost)
    try:
        greetingslist = greetings[ievent.channel]

        if greetingslist:

            if bot.type == 'xmpp' and ievent.nick.rfind('guest') != -1:
                return

            bot.say(ievent.channel, ievent.nick + ', ' + random.choice(greetingslist))

    except KeyError:
        pass

callbacks.add('JOIN', greetingcallback, greetingtest)
callbacks.add('Presence', greetingcallback, greetingtest)

def handle_greetingon(bot, ievent):
    cfg['enable'].append(ievent.channel)
    cfg.save()
    ievent.done()

cmnds.add('greeting-on', handle_greetingon, 'USER')
examples.add('greeting-on', 'enable greeting in a channel', 'greeting-on')

def handle_greetingoff(bot, ievent):
    try:
        cfg['enable'].remove(ievent.channel)
        cfg.save()
    except ValueError:
        pass

    ievent.done()

cmnds.add('greeting-off', handle_greetingoff, 'USER')
examples.add('greeting-off', 'disable  greeting in a channel', 'greeting-off')

def handle_greetingadd(bot, ievent):
    """ add greetings txt """
    if not greetings:
        ievent.reply('the greet plugin is not properly initialised')
        return
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    #username = users.getname(ievent.userhost)
    greetings.add(ievent.channel, ievent.rest)
    greetings.save()
    ievent.reply('greeting message added')

cmnds.add('greeting-add', handle_greetingadd, 'USER')
examples.add('greeting-add', "add greeting message", 'greeting-add yooo dudes')
tests.add('greetng-add boooo', 'added')

def handle_greetingdel(bot, ievent):
    """ delete greetings txt """
    if not greetings:
        ievent.reply('the greet plugin is not properly initialised')
        return
    try:
        nr = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.missing('<nr>')
        return
    #username = users.getname(ievent.userhost)
    try:
        del greetings.data[ievent.channel][nr]
    except (IndexError, KeyError):
        ievent.reply("can't delete greeting %s" % nr)
        return
    greetings.save()
    ievent.reply('greeting message %s removed' % nr)

cmnds.add('greeting-del', handle_greetingdel, 'USER')
examples.add('greeting-del', "delete greeting message", 'greeting-delete 1')
tests.add('greeting-del 1')

def handle_greetinglist(bot, ievent):
    """ list the greetings list of an user """
    if not greetings:
        ievent.reply('the greet plugin is not properly initialised')
        return
    #username = users.getname(ievent.userhost)
    result = greetings.get(ievent.channel)
    if result:
        ievent.reply("greetings: ", result, nr=0)
    else:
        ievent.reply('no greetings set')

cmnds.add('greeting-list', handle_greetinglist, 'USER')
examples.add('greeting-list', 'show greetings of user', 'greeting-list')
tests.add('greeting-list', 'boo')
