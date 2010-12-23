# me2/plugs/botevent.py
#
#

""" provide handling of host/tasks/botevent tasks. """

## me2 imports

from me2.utils.exception import handle_exception
from me2.lib.tasks import taskmanager
from me2.lib.botbase import BotBase
from me2.lib.eventbase import EventBase
from me2.utils.lazydict import LazyDict
from me2.lib.factory import BotFactory
from me2.lib.callbacks import first_callbacks, callbacks, last_callbacks

## simplejson imports

from me2.contrib.simplejson import loads

## basic imports

import logging

## boteventcb callback

def boteventcb(inputdict, request, response):
    logging.warn(inputdict)
    logging.warn(dir(request))
    logging.warn(dir(response))
    body = request.body
    logging.warn(body)
    payload = loads(body)
    try:
        botjson = payload['bot']
        logging.warn(botjson)
        cfg = LazyDict(loads(botjson))
        logging.warn(str(cfg))
        bot = BotFactory().create(cfg.type, cfg)
        logging.warn("botevent - created bot: %s" % bot.dump())
        eventjson = payload['event']
        logging.warn(eventjson)
        event = EventBase()
        event.update(LazyDict(loads(eventjson)))
        logging.warn("botevent - created event: %s" % event.dump())
        event.isremote = True
        event.notask = True
        bot.doevent(event)
    except Exception, ex: handle_exception()

taskmanager.add('botevent', boteventcb)

