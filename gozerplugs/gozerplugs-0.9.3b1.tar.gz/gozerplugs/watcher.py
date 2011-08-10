# waveplugs/watcher.py
#
#

""" watch waves through xmpp. a wave is called a channel here. """

## gozerlib imports

from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks, gn_callbacks
from gozerbot.persist.persist import PlugPersist
from gozerbot.fleet import fleet
from gozerbot.utils.log import rlog

## basic imports

import copy
import logging

cpy = copy.deepcopy

class Watched(PlugPersist):

    """ Watched object contains channels and subscribers. """

    def __init__(self, filename):
        PlugPersist.__init__(self, filename, {})
        self.data.channels = self.data.channels or {}
        self.data.whitelist = self.data.whitelist or []
        self.data.descriptions = self.data.descriptions or {}

    def subscribe(self, botname, channel, jid):

        """ subscrive a jid to a channel. """ 

        jid = unicode(jid)

        if not self.data.channels.has_key(channel):
            self.data.channels[channel] = []

        if not [botname, jid] in self.data.channels[channel]:
            self.data.channels[channel].append([botname, jid])
            self.save()

        return True

    def unsubscribe(self, botname, channel, jid):

        """ unsubscribe a jid from a channel. """ 

        try:
            self.data.channels[channel].remove([botname, unicode(jid)])

        except (KeyError, TypeError):
            return False

        self.save()
        return True

    def check(self, channel):

        """ check if channel is available (in whitelist) AND has subscribers. """

        return self.data.channels.has_key(channel)

    def subscribers(self, channel):

        """ return all subscribers of a channel. """

        try:
            return self.data.channels[channel]
        except KeyError:
            return []

    def enable(self, channel):

        """ add channel to whitelist. """

        if not channel in self.data.whitelist:
            self.data.whitelist.append(channel)
            self.save()

    def disable(self, channel):
 
        """ remove channel from whitelist. """

        try:
            self.data.whitelist.remove(channel)
        except ValueError:
            return False

        self.save()
        return True

    def available(self, channel):

        """ check if channel is on whitelist. """

        return channel in self.data.whitelist

    def channels(self, channel):
 
        """ return channels on whitelist. """ 

        res = []

        for chan, targets in self.data.channels.iteritems():

            if channel in str(targets):
                res.append(chan)

        return res

watched = Watched('channels')

def prewatchcallback(bot, event):

    return watched.check(event.channel)

def watchcallback(bot, event):

    subscribers = watched.subscribers(event.channel)

    if not subscribers:
        return

    watched.data.descriptions[event.channel] = event.title
    rlog(10, "watcher", "watcher - out - %s - %s" % (str(subscribers), event.txt))

    for item in subscribers:

        try:
            (botname, channel) = item
        except ValueError:
             continue

        orig = event.nick or event.userhost

        #if orig in [botname, bot.name]:
        #    continue

        txt = u"[%s] %s" % (orig, event.txt)

        if txt.find('] [') > 1:
            rlog(10, 'watcher', 'looping detected .. %s' % txt)
            continue

        outbot = fleet.byname(botname)

        if not outbot:
            rlog(10, 'watcher', "can't find %s bot in fleet" % botname)
            continue

        rlog(10, 'watcher', 'using %s (%s) bot' % (outbot.name, outbot.server))
        outbot.say(channel, txt)

gn_callbacks.add('BLIP_SUBMITTED', watchcallback, prewatchcallback, threaded=True)
gn_callbacks.add('PRIVMSG', watchcallback, prewatchcallback, threaded=True)
gn_callbacks.add('OUTPUT', watchcallback, prewatchcallback, threaded=True)

def handle_watcherstart(bot, event):

    if not event.rest:
        event.missing('<channel>')
        return

    channel = event.rest

    if '@' in channel:
        event.reply("you are not allowed to watch JID")
        return

    if not event.msg:
        watched.subscribe(bot.name, channel, event.channel)
    else:
        watched.subscribe(bot.name, channel, event.userhost)

    watched.enable(channel)
    event.done()

cmnds.add('watcher-start', handle_watcherstart, 'USER')

def handle_watcherstop(bot, event):

    if not event.rest:
        channel = event.channel
    else:
        channel = event.rest

    if not event.msg:
        watched.unsubscribe(bot.name, channel, event.channel)
    else:
        watched.unsubscribe(bot.name, channel, event.userhost)

    watched.disable(channel)
    event.done()

cmnds.add('watcher-stop', handle_watcherstop, 'USER')

def handle_watcherenable(bot, event):

    if not event.rest:
        channel = event.channel
    else:
        channel = event.rest

    watched.enable(channel)
    event.done()

cmnds.add('watcher-enable', handle_watcherenable, ['WATCH', 'OPER'])

def handle_watcherdisable(bot, event):

    if not event.rest:
        channel = event.channel
    else:
        channel = event.rest

    watched.disable(channel)
    event.done()
    
cmnds.add('watcher-disable', handle_watcherdisable, ['WATCH', 'OPER'])

def handle_watcherchannels(bot, event):
    chans = watched.channels(event.channel)

    if chans:
        res = []

        for chan in chans:

            try:
                res.append("%s (%s)" % (chan, watched.data.descriptions[chan]))
            except KeyError:
                res.append(chan)

        event.reply("channels watched on %s: " % event.channel, res)

cmnds.add('watcher-channels', handle_watcherchannels, ['USER'])

def handle_watcherlist(bot, event):
    event.reply("watchers for %s: " % event.channel, watched.subscribers(event.channel))

cmnds.add('watcher-list', handle_watcherlist, ['USER'])
