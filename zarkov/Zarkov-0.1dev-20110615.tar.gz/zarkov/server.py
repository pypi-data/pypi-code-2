import gevent.monkey
gevent.monkey.patch_all()

import sys
import logging
import traceback
import time

from gevent.server import StreamServer
from gevent.backdoor import BackdoorServer

logging.basicConfig()
logging.Formatter.converter=time.gmtime

from zarkov import util
from zarkov import model
from zarkov import config
from zarkov import journal

log = logging.getLogger(__name__)

log = logging.getLogger(__name__)

events = 0
agg_scheduled = False
AGG_THRESHOLD=100
mongo_retry = 0

def run(args):
    options, args = config.configure(args)
    j = journal.JournalWriter(options.journal)
    handler = StatsConnection.connection_handler(options, j)
    t = (options.bind_address, options.port)
    log.info('Starting main server on %s:%s', t[0], t[1])
    server = StreamServer(t, handler)
    if options.backdoor:
        t = (options.bind_address, options.backdoor)
        log.info('Starting backdoor server on %s:%s', t[0], t[1])
        d = dict(globals())
        d.update(locals(), handler=handler)
        s =BackdoorServer(t, locals=d)
        s.start()
    server.serve_forever()

class StatsConnection(object):

    def __init__(self, options, j, socket, address):
        log.info('Connection from %s', address)
        self._options = options
        self._j = j
        self._fp = socket.makefile()
        self._address=  address
        self.get_object = util.read_json
        self.handlers = {
            'bson':self._handle_bson,
            'json':self._handle_json,
            'login':self._handle_login,
            'event_noval':self._handle_event_noval,
            None:self._handle_event}
        self.authenticated = not self._options.password

    @classmethod
    def connection_handler(cls, options, j):
        return lambda s,a: cls(options,j,s,a).run()

    def run(self):
        while True:
            obj = self.get_object(self._fp)
            if obj is None: break
            command = obj.pop('$command', None)
            command_handler = self.handlers.get(command, None)
            if command_handler is None:
                log.warning('Unknown command %r', command)
            else:
                try:
                    command_handler(obj)
                except:
                    traceback.print_exception(*sys.exc_info())
        log.info('Close connection from %s', self._address)
        sys.stdout.flush()

    def _handle_login(self, obj):
        if obj.get('password') == self._options.password:
            self.authenticated = True
        
    def _handle_bson(self, obj):
        self.get_object = util.read_bson
        
    def _handle_json(self, obj):
        self.get_object = util.read_json
        
    def _handle_event(self, obj):
        if not self.authenticated:
            raise ValueError, "Must authenticate"
        ev = model.event(obj).make(obj)
        self._j(ev)

    def _handle_event_noval(self, obj):
        if not self.authenticated:
            raise ValueError, "Must authenticate"
        self._j(obj)
   
def _check_agg():
    global events, agg_scheduled
    events += 1
    if events > AGG_THRESHOLD and not agg_scheduled:
        log.info('Scheduling aggregation')
        agg_scheduled = True
        events = 0
        gevent.spawn(aggregate)

def aggregate():
    global agg_scheduled
    aggs = model.AggDef.query.find().all()
    log.info('Aggregate')
    #for ad in aggs: ad.incremental()
    jobs = [ gevent.spawn(ad.incremental) for ad in aggs ]
    gevent.joinall(jobs)
    model.orm_session.clear()
    agg_scheduled = False
    log.info('%d aggregations complete')
    _check_agg()

if __name__ == '__main__':
    run(sys.argv)
