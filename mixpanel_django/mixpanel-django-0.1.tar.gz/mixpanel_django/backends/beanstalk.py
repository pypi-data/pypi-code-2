#!/usr/bin/env python
#-*- coding: utf-8 -*-

from mixpanel_django.backends import dummy
import beanstalkc

class BeanstalkBackend(dummy.DummyBackend):

    def __init__(self, server, paramas):

        super(BeanstalkBackend, self).__init__(paramas)
        #self.connect = beanstalkc.Connection()
        self.host, self.port = server.split(':')
        self.paramas = paramas
        # set timeout value
        timeout = paramas.get('timeout', 30)
        import socket
        socket.setdefaulttimeout(float(timeout))
        
        # get beanstalk connection instance
        self.connect = self._do_connect()

    def _do_connect(self):
        # connect beanstalk server
        try:
            connect = beanstalkc.Connection(self.host, int(self.port), parse_yaml=False)
        except beanstalkc.SocketError:
            return None
        else:          
            # connected, then set beanstalk tube name, and watch name
            tube = self.paramas.get('tube', None)
            if tube:
                connect.use(tube)
                connect.watch(tube)
            else:
                connect.use('default')
                connect.watch('default')
            return connect
    
    def send_event(self, url):
        # check connection, did not got connection? try again
        if not self.connect:
            self.connect = self._do_connect()
            return
        
        # looks good,  put job
        try:
            self.connect.put(url)
        except beanstalkc.SocketError:
            # got error, set connect to None, until next time reconnect it
            self.connect = None
        
    def fetch_event(self):
        # check connection, did not got connection? try again
        if not self.connect:
            self.connect = self._do_connect()
            return
        
        # looks good,  reserve job
        try:
            return self.connect.reserve(0)
        except beanstalkc.SocketError:
            # got error, set connect to None, until next time reconnect it
            self.connect = None

MixpanelBackend = BeanstalkBackend
