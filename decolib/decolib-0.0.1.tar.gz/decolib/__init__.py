#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

import time
import math
import logging

class RetryFailed(Exception):
    pass

try:
    import cPickle as pickle
except:
    #Fallback to pickle
    import pickle

# Retry decorator with exponential backoff

def retry(tries, delay=3, backoff=2):
    """Retries a function or method until it complite without exeptions

    delay sets the initial delay, and backoff sets how much the delay should
    lengthen after each failure. backoff must be greater than 1, or else it
    isn't really a backoff. tries must be at least 0, and delay greater than
    0."""

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay # make mutable
            while mtries > 0:
                try:
                    rv = f(*args, **kwargs) # first attempt
                    return rv
                except Exception, ex:
                    logging.debug('Func failed, retry', exc_info=ex)
                    mtries -= 1      # consume an attempt
                    time.sleep(mdelay) # wait...
                    mdelay *= backoff  # make future wait longer
            raise RetryFailed # Ran out of tries :-(

        return f_retry # true decorator -> decorated function

    return deco_retry



def memoized(func):
    '''
    Classic memoization. Function cache results, then return objects from cache for same argumets
    '''
    memory = {}
    def memo(*args,**kwargs):
       hash = pickle.dumps((args, sorted(kwargs.iteritems())))
       if hash not in memory:
           memory[hash] = func(*args,**kwargs)
       return memory[hash]
    return memo