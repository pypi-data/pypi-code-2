# -*- coding: utf-8 -*-
"""
logglyproxy
Copyright © 2011 Evax Software <contact@evax.fr>
"""
import gevent
from gevent import monkey
monkey.patch_all()

import sys
import gevent.server
from gevent.queue import Queue

# install our keep-alive aware handler
import urllib2
from logglyproxy.keepalive import HTTPSHandler
keepalive_handler = HTTPSHandler()
opener = urllib2.build_opener(keepalive_handler)
urllib2.install_opener(opener)

from optparse import OptionParser
from ConfigParser import ConfigParser

import signal

def handle_sigterm(server):
    server.stop()

loggly_input = 'https://logs.loggly.com/inputs/'

class Syslog2Loggly(object):
    def __init__(self, key):
        self.key = key
        self.running = True
        self.msg_queue = Queue()
        gevent.spawn(self.queue_handler)

    def queue_handler(self):
        url = loggly_input+self.key
        while self.running:
            resp = urllib2.urlopen(url, data=self.msg_queue.get())
            if resp.read() != '{"response":"ok"}':
                pass

    def handler(self, socket, address):
        f = socket.makefile()
        running = True
        while running:
            try:
                msg = f.readline().strip()
                self.msg_queue.put(msg)
            except Exception, e:
                running = False

def main():
    usage = "usage: %prog -c config_file"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--config", dest="config_file",
                      help="configuration file", metavar="FILE")
    (options, args) = parser.parse_args()
    if not options.config_file:
        parser.error('you must specify a configuration file')
    config = ConfigParser()
    config.read(options.config_file)
    if not config.has_option('logglyproxy', 'apikey'):
        print 'you must provide an api key in the config file'
        sys.exit(1)
    apikey = config.get('logglyproxy', 'apikey')
    bind_address = '127.0.0.1'
    if config.has_option('logglyproxy', 'bind_address'):
        bind_address = config.get('logglyproxy', 'bind_address')
    port = 5140
    if config.has_option('logglyproxy', 'port'):
        port = config.getint('logglyproxy', 'port')
    syslog2loggly = Syslog2Loggly(apikey)
    server = gevent.server.StreamServer((bind_address, port),
                                        syslog2loggly.handler)
    gevent.signal(signal.SIGTERM, handle_sigterm, server)
    server.serve_forever()

if __name__ == '__main__':
    main()

