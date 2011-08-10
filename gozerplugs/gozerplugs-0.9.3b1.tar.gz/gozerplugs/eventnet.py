# gozerplugs/eventnet.py
#
#

## gozerbot imports

from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.utils.url import posturl, getpostdata
from gozerbot.persist.persist import PlugPersist
from gozerbot.commands import cmnds
from gozerbot.irc.monitor import outmonitor
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.rest.server import RestServer, RestRequestHandler
from gozerbot.eventbase import EventBase
from gozerbot.utils.exception import handle_exception
from gozerbot.utils.log import rlog
from gozerbot.utils.textutils import html_unescape

## simplejson imports

from simplejson import dumps

## basic imports

import socket
import re

## VARS

outurl = "http://cmndtest.appspot.com/eventnet/"

state = PlugPersist('eventnet')

if not state.data:
    state.data = {}
if not state.data.has_key('relay'):
    state.data['relay'] = []

cfg = PersistConfig()
cfg.define('enable', 0)
cfg.define('host' , socket.gethostbyname(socket.getfqdn()))
cfg.define('name' , socket.getfqdn())
cfg.define('port' , 10102)
cfg.define('disable', [])

waitre = re.compile(' wait (\d+)', re.I)
hp = "%s:%s" % (cfg.get('host'), cfg.get('port'))
url = "http://%s" % hp

## callbacks

def preremote(bot, event):

    if event.channel in state.data['relay']:
        return True

def handle_doremote(bot, event):

    if event.isremote:
        return

    posturl(outurl, {}, {'event': event.tojson() })

callbacks.add('PRIVMSG', handle_doremote, preremote, threaded=True)
outmonitor.add('eventnet', handle_doremote, preremote, threaded=True)

def handle_jabberin(bot, event):

    if event.isremote or not event.txt:
        return

    try:
        if event.txt.startswith('{'):
            e = EventBase()
            e.fromjsonstring(event.txt)
            e.isremote = True
            rlog(10, bot.name, 'got event on jabberin: %s - %s ' % (e.userhost, str(e)))
            callbacks.check(bot, e)
    except Exception, ex:
        handle_exception()
        print event.txt
        return
    
jcallbacks.add('Message', handle_jabberin)

## server part

server = None

def eventnet_POST(server, request):

    try:
        input = getpostdata(request)
        eventin = input['event']
    except KeyError, AttributeError:
        rlog(10, 'eventnet', "can't determine eventin")
        return dumps(["can't determine eventin"])

    event = EventBase()
    event.fromjsonstring(eventin)
    callbacks.check(event)
    return dumps(['ok',])

def eventnet_GET(server, request):
    try:
        path, eventin = request.path.split('#', 1)
    except ValueError:
        rlog(10, 'eventnet', "can't determine eventin")
        return dumps(["can't determine eventin", ])

    try:
        event = EventBase()
        event.fromjsonstring(eventin)
        callbacks.check(event)
    except Exception, ex:
        handle_exception()
    return dumps(['ok', ])

def startserver():

    global server 

    try:
        rlog(10, 'eventnet', 'starting server at %s:%s' % (cfg.get('host'), cfg.get('port')))
        server = RestServer((cfg.get('host'), cfg.get('port')), RestRequestHandler)

        if server:
            server.start()
            rlog(10, 'eventnet', 'running at %s:%s' % (cfg.get('host'), cfg.get('port')))
            server.addhandler('/eventnet/', 'POST', eventnet_POST)
            server.addhandler('/eventnet/', 'GET', eventnet_GET)

            for mount in cfg.get('disable'):
                server.disable(mount)

        else:
            rlog(10, 'eventnet', 'failed to start server at %s:%s' % (cfg.get('host'), cfg.get('port')))

    except socket.error, ex:
        rlog(10, 'eventnet - server', str(ex))

    except Exception, ex:
        handle_exception()

def stopserver():

    try:
        if not server:
            rlog(10, 'eventnet', 'server is already stopped')
            return

        server.shutdown()

    except Exception, ex:
        handle_exception()
        pass

## plugin init

def init():

    if cfg['enable']:
        startserver()

def shutdown():

    if cfg['enable']:
        stopserver()

def handle_eventnet_on(bot, event):

    if not event.rest:
        target = event.channel
    else:
        target = event.rest

    if not target in state.data['relay']:
        state.data['relay'].append(target)
        state.save()

    event.done()

cmnds.add('eventnet-on', handle_eventnet_on, 'OPER')

def handle_eventnet_off(bot, event):

    if not event.rest:
        target = event.channel
    else:
        target = event.rest

    if target in state.data['relay']:
        state.data['relay'].remove(target)
        state.save()
    event.done()

cmnds.add('eventnet-off', handle_eventnet_off, 'OPER')

def handle_eventnet_startserver(bot, event):
    cfg['enable'] = 1
    cfg.save()
    startserver()
    event.done()

cmnds.add('eventnet-startserver', handle_eventnet_startserver, 'OPER')

def handle_eventnet_stopserver(bot, event):
    cfg['enable'] = 0
    cfg.save()
    stopserver()
    event.done()

cmnds.add('eventnet-stopserver', handle_eventnet_stopserver, 'OPER')
