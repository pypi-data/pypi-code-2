import os
import time
from lindypy import *

def worker(ts):
    print 'worker', os.getpid(), 'start'
    while True:
        # we are interested in any tuple of four integers
        t = ts.inp((int, int, int, int))
        print 'worker', os.getpid(), 'data <-', t
        # this pretends some complex calculation
        time.sleep(1.0)
        # now grab the sum tuple and update it
        s = ts.inp(('sum', object))
        print 'worker', os.getpid(), 'sum <-', t
        ts.out(('sum', s[1]+sum(t)))
        print 'worker', os.getpid(), '-> sum', s[1]+sum(t)

def breaking_worker(ts):
    raise ValueError(55)

with tuplespace() as ts:
    # seed the tuple space with the sum tuple
    ts.out(('sum', 0))

    # start all the workers
    for i in range(5):
        ts.eval(worker)

    # push some tuples of integers into the tuple space
    ts.out((1,2,3,4))
    ts.out((4,5,6,7))
    ts.out((3,4,5,2))

    # lets pretend some complex calculation happens
    time.sleep(5.0)

    # grab the sum tuple from the tuple space
    print 'main', ts.inp(('sum', object))

    # there shouldn't be any other sum tuple
    try:
        with timeout(2):
            ts.inp(('sum', object))
    except TimeoutError:
        print 'main', "no more sums"

    # now lets try something that throws an exception
    ts.eval(breaking_worker)

    # grab the exception tuple from the tuple space
    t = ts.inp((Exception, object))
    print 'main', t

