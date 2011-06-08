from gevent import monkey, spawn
monkey.patch_all()

import sys
import logging
import traceback

from gevent.server import StreamServer
from gevent.backdoor import BackdoorServer

logging.basicConfig()

from zarkov import util
from zarkov import model
from zarkov import config

events = 0
agg_scheduled = False
AGG_THRESHOLD=1000

def run(args):
    options, args = config.configure(args)
    handler = StatsConnection.connection_handler(options)
    t = (options.bind_address, options.port)
    print 'Starting main server on %s:%s' % t
    server = StreamServer(t, handler)
    if options.backdoor:
        t = (options.bind_address, options.backdoor)
        print 'Starting backdoor server on %s:%s' % t
        d = dict(globals())
        d.update(locals(), handler=handler)
        s =BackdoorServer(t, locals=d)
        s.start()
    server.serve_forever()

class StatsConnection(object):

    def __init__(self, options, socket, address):
        print 'Connection from ', address
        self._options = options
        self._fp = socket.makefile()
        self._address=  address
        self.get_object = util.read_json
        self.handlers = {
            'bson':self._handle_bson,
            'json':self._handle_json,
            'login':self._handle_login,
            'nop':self._handle_nop,
            'echo':self._handle_echo,
            'event_noval':self._handle_event_noval,
            None:self._handle_event}
        self.authenticated = not self._options.password
        self.c_event = model.doc_session.db.event

    @classmethod
    def connection_handler(cls, options):
        return lambda s,a: cls(options,s,a).run()

    def run(self):
        while True:
            obj = self.get_object(self._fp)
            if obj is None: break
            command = obj.pop('$command', None)
            command_handler = self.handlers.get(command, None)
            if command_handler is None:
                print 'Unknown command %r' % command
            else:
                try:
                    command_handler(obj)
                except:
                    traceback.print_exception(*sys.exc_info())
        print 'Close', self._address
        sys.stdout.flush()

    def _handle_login(self, obj):
        if obj.get('password') == self._options.password:
            self.authenticated = True
        
    def _handle_bson(self, obj):
        self.get_object = util.read_bson
        
    def _handle_json(self, obj):
        self.get_object = util.read_json
        
    def _handle_echo(self, obj):
        print obj

    def _handle_nop(self, obj):
        pass

    def _handle_event(self, obj):
        if not self.authenticated:
            raise ValueError, "Must authenticate"
        ev = model.event(obj).make(obj)
        save_noval(self.c_event, ev)

    def _handle_event_noval(self, obj):
        if not self.authenticated:
            raise ValueError, "Must authenticate"
        save_noval(self.c_event, obj)
   
def _check_agg():
    global events, agg_scheduled
    events += 1
    if events > AGG_THRESHOLD and not agg_scheduled:
        print 'Scheduling agg'
        agg_scheduled = True
        events = 0
        spawn(aggregate)

def save_noval(collection, obj):
    collection.save(obj, safe=False)
    _check_agg()

def aggregate():
    global agg_scheduled
    for ad in model.AggDef.query.find().all():
        r = ad.incremental()
        print 'Agg %s: %r' % (ad.name, r)
    model.orm_session.clear()
    agg_scheduled = False
    print 'Aggregation completed'
    _check_agg()

if __name__ == '__main__':
    run(sys.argv)
