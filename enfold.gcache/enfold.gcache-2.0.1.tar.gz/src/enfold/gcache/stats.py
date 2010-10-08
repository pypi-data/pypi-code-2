################################################################################
# Copyright: Enfold Systems, LLC
# $Id: httpcache.py 4198 2010-08-11 17:04:08Z nikolay $
#
# A simple cache statistics.
#
################################################################################
import copy

class Stats(object):
    """ Stats for the cache

    >>> class Cache(dict):
    ...     @property
    ...     def size(self):
    ...         return len(self)

    >>> stats = Stats(Cache())

    >>> print stats == Stats(Cache())
    True

    >>> print stats
    Cache statistics:
      gets: 0, hits: 0 (0 validated), misses: 0 (0 uncachable)
      hitrate: 0% (0% excluding validations)
      size: 0 bytes, 0 items

    >>> stats.add_get()
    >>> stats.add_hit(False)
    >>> stats.add_get()
    >>> stats.add_hit(True)
    >>> stats.add_get()
    >>> stats.add_uncachable()

    >>> print stats
    Cache statistics:
      gets: 3, hits: 2 (1 validated), misses: 1 (1 uncachable)
      hitrate: 66% (50% excluding validations)
      size: 0 bytes, 0 items

    >>> s1 = stats.copy()
    >>> print s1 == stats
    True

    >>> stats is s1
    False
    """

    def __init__(self, cache):
        self.hits_absolute = 0
        self.hits_validated = 0
        self.gets = 0
        self.uncachable = 0
        self.cache = cache

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def copy(self):
        return copy.copy(self)

    def calc_misses(self):
        return self.gets - self.hits_absolute - self.hits_validated

    def add_hit(self, was_validated):
        if was_validated:
            self.hits_validated += 1
        else:
            self.hits_absolute += 1

    def add_get(self):
        self.gets += 1

    def add_uncachable(self):
        self.uncachable += 1

    def __str__(self):
        cache_size = self.cache.size
        cache_len = len(self.cache)
        misses = self.calc_misses()
        hits_total = self.hits_absolute + self.hits_validated
        if hits_total + misses == 0:
            hitrate_total = 0
        else:
            hitrate_total = int(100 * hits_total / (hits_total + misses))
        if self.hits_absolute + misses == 0:
            hitrate_validated = 0
        else:
            hitrate_validated = int(100 * self.hits_absolute /
                                    (self.hits_absolute+ misses))
        vals = dict()
        vals.update(self.__dict__)
        vals.update(locals())
        return \
"""Cache statistics:
  gets: %(gets)d, hits: %(hits_total)d (%(hits_validated)d validated), misses: %(misses)d (%(uncachable)d uncachable)
  hitrate: %(hitrate_total)d%% (%(hitrate_validated)d%% excluding validations)
  size: %(cache_size)d bytes, %(cache_len)d items""" % vals
