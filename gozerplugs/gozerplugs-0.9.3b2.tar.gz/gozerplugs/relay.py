# plugs/relay.py
#
#

"""
 the bot can relay between different bots both IRC and Jabber ones.
 relay uses the following format.

 <botname> <channel> <botname> <channel>

 <------ from -----> <------- to ------>
"""

__copyright__ = 'this file is in the public domain'
__gendoclast__ = ['relay-del', ]

from gozerbot.utils.generic import convertpickle, jsonstring
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.fleet import fleet
from gozerbot.irc.monitor import saymonitor
from gozerbot.xmpp.monitor import xmppmonitor
from gozerbot.datadir import datadir
from gozerbot.persist.pdol import Pdol
from gozerbot.plughelp import plughelp
from gozerbot.ignore import shouldignore
from gozerbot.generic import rlog
from gozerbot.threads.thr import start_new_thread
from gozerbot.tests import tests

from simplejson import loads

import time, os

plughelp.add('relay', 'relay between fleet bots or channels')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'relay', \
datadir + os.sep + 'plugs' + os.sep + 'relay' + os.sep + 'relay')

class Relay(Pdol):

    """ relay is implemented as a pickled dict of lists """

    def check(self, botname, channel, txt, fromm=None):
        """ check if we relay on (botname, channel) .. if so do output """
        channel = channel
        mainbot = fleet.byname(botname)
        if not mainbot:
            rlog(10, 'relay', "can't find %s bot in fleet" % botname)
            return
        marker2 = '<%s>' % (mainbot.channels.getnick(channel) or mainbot.nick)

        if marker2 in txt:
            return

        indexstring = jsonstring((botname, channel))
        index = loads(indexstring)

        if self.data.has_key(indexstring):

            for i in self.data[indexstring]:

                if i != index:
                    bot = fleet.byname(i[0])
                    chan = i[1]

                    if bot:

                        if bot.jabber:
                             marker = '<%s>' % bot.channels.getnick(chan)
                        else:
                             marker = '<%s>' % bot.nick

                        if marker in txt: 
                            return

                        if not bot.stopped:
                            time.sleep(1)
                            bot.outputnolog(i[1], txt, 'msg', fromm=fromm)

    def wouldrelay(self, botname, channel):

        """ check if (botname, channel) would relay """

        return self.data.has_key(jsonstring((botname, channel)))

    def channels(self, botname):

        """ show channels that are relayed on bot """

        result = []

        for i in self.data.keys():

            if i[0] == botname:
                result.append(i[1])

        return result

def init():
    """ called after reload """
    saymonitor.start()
    xmppmonitor.start()
    saymonitor.add('relay', saycb, prerelaysay, True)
    xmppmonitor.add('relay', jabbersaycb, jabberprerelaysay, True)
    return 1
    
relay = Relay(datadir + os.sep + 'plugs' + os.sep + 'relay' + os.sep + 'relay')
if not relay.data:
    upgrade()
    relay = Relay(datadir + os.sep + 'plugs' + os.sep + 'relay' + os.sep + 'relay')

jabberjoined = {}

def size():

    """ return number of relays """

    return len(relay.data)

def prerelay(bot, ievent):

    """ precondition """

    if not ievent.txt:
        return 0

    if shouldignore(ievent.userhost):
        return 0

    go = relay.wouldrelay(bot.name, ievent.channel)

    if go:
        ievent.isrelay = True

    return go

def cbrelayquit(bot, ievent):

    """ relay quit callback """

    time.sleep(1)
    nick = ievent.nick

    if nick in bot.splitted:
        return

    try:

        for i in bot.userchannels[nick]:

            if i in bot.state['joinedchannels']:
                relay.check(bot.name, i, "%s (%s) quit %s - %s" % \
(ievent.nick, ievent.userhost, bot.server, ievent.txt))

    except KeyError:
        rlog(10, 'relay', 'missing %s in userchannels' % nick)

callbacks.add('QUIT', cbrelayquit, nr=0, threaded=True)

def cbrelaykick(bot, ievent):

    """ relay kick callback """

    relay.check(bot.name, ievent.channel, "%s kicked %s from %s (%s) - %s" % \
(ievent.nick, ievent.arguments[1], ievent.channel, bot.server, ievent.txt))

callbacks.add('KICK', cbrelaykick, prerelay, threaded=True)

def cbrelaynick(bot, ievent):

    """ relay nick callback """

    nick = ievent.nick

    try:

        for i in bot.userchannels[nick]:

            if i in bot.state['joinedchannels']:
                relay.check(bot.name, i, "%s is now known as %s" % \
(ievent.nick, ievent.txt))

    except KeyError:
        rlog(10, 'relay', 'missing %s in userchannels' % nick)

callbacks.add('NICK', cbrelaynick, threaded=True)

def cbrelaytopic(bot, ievent):

    """ relay topic callback """

    relay.check(bot.name, ievent.channel, "%s changed topic to %s" % (ievent.nick, ievent.txt))

callbacks.add('TOPIC', cbrelaytopic, prerelay, threaded=True)

def cbrelaymode(bot, ievent):

    """ callback for MODE events """

    relay.check(bot.name, ievent.channel, "mode change on %s by %s \
(%s): %s" % (bot.server, ievent.nick, ievent.userhost, ievent.postfix))

callbacks.add('MODE', cbrelaymode, prerelay, threaded=True)

def cbrelaypriv(bot, ievent):

    """ PRIVMSG relay callback """

    t = ievent.origtxt or ievent.txt
    t = t.strip()

    if not t:
        return

    if t[0] == '\001' and t.find('ACTION') != -1:
        result = "<%s> *** %s" % (ievent.nick, t[8:-1])
    else:
        result = "<%s> %s" % (ievent.nick, t)

    relay.check(bot.name, ievent.channel, result, fromm=ievent.userhost)

callbacks.add('PRIVMSG', cbrelaypriv, prerelay, threaded=True)

def cbMessage(bot, msg):

    """ jabber relay message callback """

    t = msg.origtxt or msg.txt
    t = t.strip()

    if not t:
        return

    if msg.usercmnd and not msg.groupchat:
        return

    if bot.google:
        result = "<%s> %s" % (msg.userhost, t)
    else:
        result = "<%s> %s" % (msg.nick, t)

    relay.check(bot.name, msg.channel, result, fromm=msg.userhost)

jcallbacks.add('Message', cbMessage, prerelay, threaded=True)

def cbPresence(bot, msg):

    """ jabber relay presence callback """

    result = None
    got = False

    if msg.type == 'unavailable':
        result = "%s (%s) left %s" % (msg.nick, msg.userhost, msg.channel)

        try:
            jabberjoined[msg.channel].remove(msg.nick)
        except (ValueError, KeyError):
            pass

    elif msg.joined:

        try:

            if msg.nick in jabberjoined[msg.channel]:
                got = True
            else:
                got = False

        except KeyError:
            got = False

        if not got:

            if not jabberjoined.has_key(msg.channel):
                jabberjoined[msg.channel] = []

            jabberjoined[msg.channel].append(msg.nick)

            if bot.timejoined.has_key(msg.channel):

                if time.time() - bot.timejoined[msg.channel] > 10:
                    result = "%s (%s) joined %s" % (msg.nick, msg.userhost, msg.channel)

    if result:
        relay.check(bot.name, msg.channel, result)

jcallbacks.add('Presence', cbPresence, prerelay, threaded=True)

def cbrelayjoin(bot, ievent):

    """ JOIN relay callback """

    if ievent.nick in bot.splitted:
        return

    relay.check(bot.name, ievent.channel, "%s (%s) joined %s on %s" % \
(ievent.nick, ievent.userhost, ievent.channel, bot.server))

callbacks.add('JOIN', cbrelayjoin, prerelay, nr=0, threaded=True)

def cbrelaypart(bot, ievent):

    """ PART relay callback """

    relay.check(bot.name, ievent.channel, "%s left %s on %s" % \
(ievent.nick, ievent.channel, bot.name))

callbacks.add('PART', cbrelaypart, prerelay, threaded=True)

def prerelaysay(botname, printto, txt, who, how, fromm):

    """ precondition on bot.say callbacks """

    return relay.wouldrelay(botname, printto)

def saycb(botname, printto, txt, who, how, fromm):

    """ callback for bots output """

    relay.check(botname, printto, "<bot> %s" % txt, fromm=fromm)

def jabberprerelaysay(bot, jmsg):

    """ precondition on bot.say callbacks """

    if jmsg:
        return relay.wouldrelay(bot.name, jmsg.to.split('/')[0])

def jabbersaycb(bot, jmsg):

    """ callback for bots output """

    if jmsg.botoutput and not jmsg.groupchat:
        return

    t = jmsg.txt or jmsg.origtxt

    if not t:
        return

    try:
        chan = jmsg.to.split('/')[0]
        relay.check(bot.name, chan, "<bot> %s" % t, fromm=bot.name)

    except AttributeError:
        handle_exception()
        return
        
def handle_relaylist(bot, ievent):

    """ realy-list .. list all relays """

    result = []

    for item, value in relay.data.iteritems():
        tempstr = ""

        for relayto in value:
            tempstr += "[%s,%s] .. " % (relayto[0], relayto[1])

        tempstr = tempstr[:-4]
        result.append("%s => %s" % (item, tempstr))

    if result:
        ievent.reply(result, dot=' || ')
    else:
        ievent.reply('no relays')

cmnds.add('relay-list', handle_relaylist, 'OPER')
examples.add('relay-list', 'list the relays', 'relay-list')
tests.add('relay-list')

def handle_relayadd(bot, ievent):

    """ relay-add <botname> <channel> <botname> <channel> .. add a relay """

    try:
        (botnamefrom, channelfrom, botnameto, channelto) = ievent.args
    except ValueError:
        ievent.missing('<botnamefrom> <channelfrom> <botnameto> <channelto>')
        return
    relay[jsonstring([botnamefrom, channelfrom])] = [botnameto, channelto]
    relay.save()
    ievent.reply('relay added')

cmnds.add('relay-add', handle_relayadd, 'OPER')
examples.add('relay-add', 'relay-add <botname> <channel> <botname> \
<channel> .. add bot/channel to relay', 'relay-add main #dunkbots test \
#dunkbots')
tests.add('relay-add default #dunkbots irc #dunkbots')

def handle_relaydel(bot, ievent):
    """ relay-del <botname> <channel> <botname> <channel> .. delete a relay """
    try:
        (botnamefrom, channelfrom, botnameto, channelto) = ievent.args
    except ValueError:
        ievent.missing('<botnamefrom> <channelfrom> <botnameto> <channelto>')
        return
    try:
        relay[jsonstring([botnamefrom, channelfrom])].remove([botnameto, \
channelto])
    except (KeyError, ValueError, AttributeError):
        ievent.reply("there is no %s %s - %s %s relay" % \
(botnamefrom, channelfrom, botnameto, channelto))
        return
    if len(relay[jsonstring([botnamefrom, channelfrom])]) == 0:
        del relay[jsonstring([botnamefrom, channelfrom])]
    relay.save()
    ievent.reply('relay deleted')

cmnds.add('relay-del', handle_relaydel, 'OPER')
examples.add('relay-del', 'relay-del <botname> <channel> <botname> \
<channel> .. delete bot/channel from relay', 'relay-del main #dunkbots \
test #dunkbots')
tests.add('relay-del default #dunkbots irc #dunkbots')
