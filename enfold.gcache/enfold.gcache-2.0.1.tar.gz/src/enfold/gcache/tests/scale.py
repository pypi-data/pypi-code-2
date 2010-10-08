#$Id: scale.py 4292 2010-08-30 19:57:37Z nikolay $
#Copyright: Enfold Systems Ltd

# Simple tests to see how the cache scales.  Also watch the memory-footprint
# using taskmon etc.
from time import sleep, clock
import tempfile
import unittest
import sys, os
import shutil
import new
import datetime
import random
import logging

from enfold.gcache.cache import Cache, metadata, now
from enfold.gcache.diskstorage import DiskStorage

logger = logging.getLogger()
hdlr = logging.FileHandler('test.log')
fmt = logging.Formatter(logging.BASIC_FORMAT)
hdlr.setFormatter(fmt)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

TestCase = unittest.TestCase

def test_num_items(num_items):
    cache = Cache(logger=logger, max_len=num_items+1)
    max_value = num_items * 2
    for i in xrange(num_items):
        cache.set(random.randint(0, max_value), (None, "x"))
    start = clock()
    num_tries = 100
    for i in xrange(num_tries):
        try:
            cache[random.randint(0, max_value)]
        except KeyError:
            pass
    took = clock() - start
    start = clock()
    for i in xrange(num_tries):
        cache.set(random.randint(0, max_value), (None, "x"))
    took_set = clock() - start

    print "With %d items in the cache, average lookup time was %.5g ms, set time was %.5g ms" % \
          (num_items, took*1000/num_tries, took_set*1000/num_tries)
    print cache.stats
    cache.close()

def test_scale():
    for i in (10, 100, 1000, 10000, 20000, 50000, 80000, 500000):
        test_num_items(i)
        try:
            import gc
            gc.collect()
            print "%d Python references alive..." % sys.gettotalrefcount()
        except AttributeError:
            pass

if __name__=='__main__':
    test_scale()
