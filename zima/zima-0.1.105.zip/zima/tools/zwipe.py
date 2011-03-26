#!/usr/bin/python
# -*- coding: utf-8 -*-
# Наполняет имиджборду содержимым
import re
import os
import sys
import time
import random

sys.path.append(os.path.abspath('..'))

import glob
from utils import ThreadPool
from names import reftitle
from httppost import httppost

cron = None
textdata, attaches, prefixes = [], [], []

def makemsg(parent):
    def pfx():
        return random.choice(['', '', '/s/', '/b/', '', '/'])
    links = []
    for l in xrange(0, random.randint(0, 3)):
        links.append(reftitle('', pfx(), int(parent) + abs(random.randint(-1000, 1000))))
    uploads = []
    if random.randint(0,1):
       for i in xrange(0, random.randint(0, 3)):
           fn = random.choice(attaches)
           uploads.append(('file', fn, open(fn, 'rb').read()))
    if parent <> 0:
        parentText = ' %d :parent' % parent
    else:
        parentText = ''
    params = {
        'message': '.. %s thread :goto\n\n%s\n%s' % (parentText, random.choice(textdata), ', '.join(links))
    }
    return params, uploads

def replier(addr, thread):
    httppost(addr, *makemsg(thread))

def threader(addr, length, count):
    reply = httppost(addr, *makemsg(0))
    m = re.search('URL\=\D+(\d+)', reply)
    if m and m.group(1):
        print m.group(1)
        for i in xrange(0, length):
            cron.schedule(replier, addr, int(m.group(1)))
        if count > 0:
            cron.schedule(threader, addr, length, count - 1)
    else:
        print reply

def start(path, getpath, workersCount, data_fname):
    global textdata, attaches, prefixes, cron
    textdata = open(data_fname).read().split('Report')
    attaches = list(glob.iglob('*.jpg'))
    prefixes = ['', '/s', '/b']
    cron = ThreadPool(workersCount)
    cron.schedule(threader, path, 50, 20)

if __name__ == '__main__':
    import glob
    def f(path):
        host = '127.0.0.1'
        port = 8070
        start('http://%s:%s/%spost' % (host, port, path),
             'http://%s:%s/%s' % (host, port, path),
            10,
            glob.glob('*.txt')[0])
    f('')
    #f('s/')
    #f('b/')

