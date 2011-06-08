import sys
import time
from contextlib import contextmanager 

import gevent

n = int(sys.argv[1])
c = int(sys.argv[2])
if len(sys.argv) > 3:
    password = sys.argv[3]
else:
    password=None
mode='bson'

from zarkov import model
from zarkov import config
from zarkov import helpers as h
from zarkov.client import ZarkovClient

def runner(n):
    cli = ZarkovClient('127.0.0.1', 6543, password=password, mode=mode)
    for x in xrange(n):
        cli.event_noval(
            type='foo',
            context=dict(
                neighborhood='projects',
                project='test',
                tool='wiki',
                app='home',
                user='admin1'))

@contextmanager
def timing():
    timer = [0]
    start = time.time()
    yield timer
    stop = time.time()
    timer[0] = stop-start

def main():
    config.configure()

    h.setup_time_aggregates()

    jobs = [
        gevent.spawn(runner, n//c)
        for x in xrange(c) ]
    with timing() as t:
        gevent.joinall(jobs)

    print '%d events in %.2f s, %.0f r/s' % (
        n, t[0], float(n)/(t[0]))
    return

    agg_defs = model.AggDef.query.find().all()
    for ad in agg_defs:
        print 
        print '=== Aggregate:', ad.name, '==='
        # updated = ad.incremental()
        # updated = ad.full()
        for doc in ad.collection.find().sort('_id'):
            print '%8s: %s' % (doc['_id'], doc['value'])

if __name__ == '__main__':
    main()
