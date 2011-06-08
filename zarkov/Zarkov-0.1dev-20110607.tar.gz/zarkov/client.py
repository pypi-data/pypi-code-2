from datetime import datetime

from gevent import socket

from zarkov import util
from zarkov import model

class ZarkovClient(object):

    def __init__(self, addr, port, password=None, mode='bson'):
        self._socket = socket.socket()
        self._socket.connect((addr,port))
        self._fp = self._socket.makefile()
        self.put_object = util.write_json
        if mode == 'bson':
            self.bson()
        if password:
            self.login(password)

    def login(self, password):
        self._command('login', password=password)

    def bson(self):
        self._command('bson')
        self.put_object = util.write_bson
        
    def json(self):
        self._command('json')
        self.put_object = util.write_json
        
    def echo(self, **kw):
        self.put_object(self._fp, kw)

    def event(self, type, context, extra=None):
        self.put_object(self._fp, dict(
                type=type, context=context, extra=extra))

    def event_noval(self, type, context, extra=None):
        obj = model.event.make(dict(
                type=type,
                context=context,
                extra=extra))
        obj['$command'] = 'event_noval'
        self.put_object(self._fp, obj)

    def _command(self, cmd, **kw):
        d = dict(kw)
        d['$command'] = cmd
        self.put_object(self._fp, d)
