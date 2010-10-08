################################################################################
# Copyright: Enfold Systems, LLC
# $Id: cache.py 4292 2010-08-30 19:57:37Z nikolay $
#
# A basic cache implementation.
#
################################################################################
import sys, os, time, datetime, copy
from threading import RLock, Event, Thread

from enfold.gcache import getLogger
from enfold.gcache.priqueue import PQueue

secs_per_day = 3600 * 24

from stats import Stats
from utils import now, fixupTimeDelta
from interfaces import Uncachable, ValidationGotNewItem


class metadata(object):
    """ This is class for the metadata managed by the cache.
    It is *not* the cached data."""

    __slots__ = ('size', 't_verified', 't_modified', 't_stale', 't_evict',
                 't_accessed', 'storage_id')

    def __init__(self, size, t_modified,
                 t_stale = None, t_verified = None, t_evict = None):
        # Note: these instances may be pickled, so you can't rely on this
        # method to initialize items that are already in a cache!

        self.size = size

        # t_modified is no longer used by the impl - the 'verified time' is
        # used in all staleness etc calcs (even if something was modified a
        # year ago, so long as it validated recently it is good to use)
        if t_verified is None:
            t_verified = t_modified
        self.t_verified = t_verified
        self.t_modified = t_modified
        self.t_stale = t_stale
        self.t_evict = t_evict
        self.t_accessed = None

        # self.storage_id is a nod to a "Storage" limitation - diskstorage
        # needs an extra meta-data item (the filename), but metadata is part
        # of the cache, not the storage.  Can see the potential for other
        # storages to require something similar (even if not a filename).
        self.storage_id = None

    def __getstate__(self):
        return tuple([getattr(self, s, None) for s in self.__slots__])

    def __setstate__(self, data):
        # init stuff that has been added since life started...
        self.storage_id = None

        # and load whatever is actually in the pickle
        for s, v in zip(self.__slots__, data):
            setattr(self, s, v)

    def __str__(self):
        vals = {}
        for s in self.__slots__:
            vals[s] = getattr(self, s)
        return "Metadata("\
            "size: %(size)d, acc: %(t_accessed)s, mod: %(t_modified)s" \
            ", ver: %(t_verified)s, stale: %(t_stale)s, evict: %(t_evict)s)" %vals


class NoMetadata(metadata):
    """ To be used when no metadata is available - data is considered
    fresh "now", and expires at the default rate.

    >>> md = NoMetadata("test")
    >>> md.size
    4
    >>> md = NoMetadata(None)
    >>> md.size
    0
    """

    def __init__(self, data):
        try:
            data_len = len(data)
        except TypeError:
            data_len = 0

        super(NoMetadata, self).__init__(data_len, now())


class CacheStorage(dict):
    """ A class providing a dictionary-like interface - classes may override to
    provide persistance.
    XXX - this is broken in that it confuses metadata with item data.
    get_meta/update_meta and the fact that diskstorage also hides updating
    metadata behind the dict-like methods (eg, __setitem__) """

    def __init__(self):
        self.purge_list = []

    def open(self):
        pass

    def close(self):
        pass

    def flush(self):
        pass

    def maintain(self):
        pass

    def get_meta(self, key):
        """ The extra methods our cache wants. Fetch *just* the meta-data. """
        return self[key][0]

    def query(self, *args, **kw):
        raise KeyError()

    def update_meta(self, key, new_meta):
        """ Update *just* the metadata for an existing item. """
        old_key, data = self[key]
        self[key] = new_meta, data

    def purge_iter(self):
        """ Deal with a "purge list """
        for item in self.purge_list:
            yield item

    def purge_add(self, value):
        self.purge_list.append(value)

    def purge_remove(self, value):
        self.purge_list.remove(value)

    def iterkeys(self, start = None):
        """ A specialized key iterator: if param is given, start the iteration
        from the first matching key """
        for k in sorted(dict.iterkeys(self)):
            if start is not None and k < start:
                continue
            yield k


# A sentinal to know a value hasn't been set.
NoValue = object()


class Cache(object):

    # Attribute names that can be set via kw args to 'configure' and
    # '__init__', and the default value.
    attrs = {
        'logger':             None, # The logger to write to
        'max_size':           None, # max number of bytes stored in the cache data
        'max_len':            50000,# max number of items in the cache.
        'max_transient_len':  None, # max temp length
        'max_transient_size': None, # max temp size
        'default_age':        60,   # if no expiry info given, when do we check freshness?
        'max_age':            None, # If expiry is given, the largest we use
        'evict_factor':       0.5,  # How long after the item is stale should we keep it for?
        'max_item_size':      None, # Largest size of an item we store
        'track_accessed':     True, # Is a 'least-recently-accessed' queue maintained?
                                    # Not tracking this makes for much faster access, but
                                    # means items are evicted purely based on age.
        'enable_background_purging': False, # Do we start a background thread
                                            # to support time-consuming 'purge'
                                            # operations?
    }

    def __init__(self, provider, storage, **kw):
        # NoValue is a nod to tools like pychecker, which complains if
        # attributes haven't been set, plus our configure code that applies
        # default values if they haven't already been overridden.
        self.max_len = NoValue
        self.max_size = NoValue
        self.max_item_size = NoValue
        self.track_accessed = NoValue
        self.provider = provider
        self.queue_accessed = PQueue()
        self.queue_evict = PQueue()
        self.size = 0
        self.data = storage

        self.stats = Stats(self)
        self.lock = self.createLock()
        self.dirty = False

        # ready to roll - set the base options.
        self.configure(**kw)

        # Now install the data into the cache.
        for key in storage.iterkeys():
            try:
                # don't actually load the data - that takes ages!
                meta = storage.get_meta(key)
            except:
                self.logger.exception(
                    "Failed to load initial key '%s' from storage", key)
                try:
                    del storage[key]
                except:
                    pass
                continue
            self.size += meta.size
            self.queue_evict[key] = meta.t_evict
            if self.track_accessed:
                self.queue_accessed[key]=meta.t_accessed

        self.logger.info("Cache initialized with %d items", len(self.data))

        # persistant cache options may have changed,
        # so the loaded cache may be too large
        self.maintain()

        # setup purging
        self._purge_event = None # this is the magic flag - none == disabled
        if self.enable_background_purging:
            self._purge_event = Event()
            self._purge_thread = Thread(target = self._purge_thread_function)
            self._purge_thread.setDaemon(True) # so we don't hang if not closed!
            self._purge_thread.start()

    def __len__(self):
        return len(self.data)

    def createLock(self):
        return RLock()

    def configure(self, **kw):
        for attr, def_val in self.attrs.items():
            if getattr(self, attr, NoValue) is NoValue:
                setattr(self, attr, def_val)

        for attr, val in kw.items():
            if not attr in self.attrs:
                raise RuntimeError("Invalid config option '%s'" % (attr,))
            setattr(self, attr, val)

        # now fixup the options.
        if self.logger is None:
            self.logger = getLogger()

        self.max_transient_len = self.max_transient_len or self.max_len
        self.max_transient_size = self.max_transient_size or self.max_size
        self.max_age = fixupTimeDelta(self.max_age)
        self.default_age = fixupTimeDelta(self.default_age)

        if self.max_age and self.default_age <= self.max_age:
            raise RuntimeError(
                "Default age can not be greater than the maximum age!")

        if not self.track_accessed and self.queue_accessed is not None:
            self.queue_accessed = None

    def close(self):
        self.lock.acquire()
        try:
            if self.data is not None:
                self.data.close()
                self.data = None

                # shutdown purging - set the event while the lock is held, then
                # wait for that thread to terminate.
                if self._purge_event is not None:
                    self._purge_event.set()

            self.stats = None # break circle
        finally:
            self.lock.release()

        if self._purge_event is not None:
            self._purge_thread.join(5)
            self._purge_event = None
            self._purge_thread = None

    def flush(self):
        self.logger.debug("Flush starting")
        self.lock.acquire()
        start = now()
        try:
            self.data.flush()
            self.dirty = False
        finally:
            self.lock.release()
        self.logger.info("Cache flush took %s", now()-start)

    def clear(self):
        """ Can't use simple dict iteration as we modify it.  Can't pop*(), as
        the key must remain in the dict.  Really don't want to use keys() -
        that sucks for a huge cache.  So we do things painfully... """
        rc = False
        while len(self.data):
            rc = True # we did something!
            for k in self.data.iterkeys():
                self.dispose(k)
                break # only do 1 item each loop!
        return rc

    def fixupMeta(self, meta, now):
        if not meta.t_verified:
            meta.t_verified = now

        if not meta.t_stale:
            meta.t_stale = meta.t_verified + self.default_age

        if self.max_age and (meta.t_stale - meta.t_verified > self.max_age):
            meta.t_stale = meta.t_verified + self.max_age

        if not meta.t_evict:
            # Not sure how to do this correctly!  This is good enough
            age_delta = meta.t_stale - meta.t_verified
            age = age_delta.days * secs_per_day + age_delta.seconds
            meta.t_evict = meta.t_stale + \
                datetime.timedelta(seconds=age * self.evict_factor)

        meta.t_accessed = now
        # If a provider explicitly provides an expiry date in the past, this
        # assertion will blow.  A stale date in the past is OK.
        #assert meta.t_stale >= meta.t_verified, meta
        # Ditto for eviction
        #assert meta.t_evict >= meta.t_stale, meta

    def dispose(self, key):
        # As per comments in _get, must also lock even to *access* data.
        self.lock.acquire()
        try:
            try:
                meta = self.data.get_meta(key)
            except KeyError:
                # Not in the cache!
                self.logger.debug(
                    "Unable to dispose of item - not in the cache (%s)", key)
                return False

            self.logger.debug("Disposing of key '%s'", key)
            del self.data[key]
            if self.track_accessed:
                del self.queue_accessed[key]
            del self.queue_evict[key]
            self.size -= meta.size
            assert self.size >= 0, self.size # a negative size spells trouble.
            assert meta.size >= 0, meta.size # here too!
            self.dirty = True
            return True
        finally:
            self.lock.release()

    def do_maintain(self, to_size, to_len):
        lnow = now()
        max_size = to_size or self.size
        max_len = to_len or len(self.data)
        self.logger.debug(
            "Maintenance starting with %d bytes (target=%s), "
            "%d items (target=%s)", self.size, max_size, len(self.data), max_len)

        # Everything past evict time gets thrown out first.
        while self.size > max_size or len(self.data) > max_len:
            # Cache must be stable between peeking and disposing!
            self.lock.acquire()
            try:
                value, key = self.queue_evict.peek()
                # If we are not maintaining the 'last accessed' queue, we must
                # continue here until we hit the condition.
                if self.track_accessed and value > lnow:
                    break
                self.logger.debug("Evicting '%s' as past evict time (%d/%d)",
                                  key, self.size, len(self.data))
                self.dispose(key)
            finally:
                self.lock.release()

        if self.track_accessed:
            # Keep throwing things out via last accessed until
            # we hit our condition
            while self.size > max_size or len(self.data) > max_len:
                self.lock.acquire()
                try:
                    value, key = self.queue_accessed.peek()
                    self.logger.debug(
                        "Evicting '%s' as oldest accessed (%d/%d)",
                        key, self.size, len(self.data))
                    self.dispose(key)
                finally:
                    self.lock.release()

        self.data.maintain()

        self.logger.debug(
            "Maintenance complete with %d bytes, %d items",
            self.size, len(self.data))

    def maintain(self, to_size = None, to_len = None):
        if to_size is None:
            to_size = self.max_size
        if to_len is None:
            to_len = self.max_len
        self.do_maintain(to_size, to_len)

    def should_maintain(self):
        # Eeek - this sucks - in the worst case accessing the DB may be
        # undergoing a repair operation - we must lock :(
        self.lock.acquire()
        try:
            max_size = self.max_size or self.size
            cur_len = len(self.data)
            max_len = self.max_len or cur_len
            return self.size > max_size or cur_len > max_len
        finally:
            self.lock.release()

    def do_set(self, key, (meta, data)):
        if meta is None:
            meta = NoMetadata(data)

        if self.max_item_size and meta.size > self.max_item_size:
            self.logger.info(
                "Item of size %d is greater than max allowed (%d) - not storing",
                meta.size, self.max_item_size)
            return False

        if self.max_size and meta.size > self.max_size:
            self.logger.info(
               "Item of size %d is greater than cache maximum (%d) - not storing",
               meta.size, self.max_size)
            return False

        assert meta.size >= 0, meta.size # that would screw us!

        lnow = now()
        self.fixupMeta(meta, lnow)
        self.dispose(key)
        self.logger.info("Cache set of key '%s'->%s", key, meta)
        self.data[key] = meta, data
        self.queue_evict.insert(meta.t_evict, key)
        if self.track_accessed:
            self.queue_accessed.insert(meta.t_accessed, key)
        self.size += meta.size
        self.dirty = True
        self.maintain(self.max_transient_size, self.max_transient_len)
        return True

    def set(self, *args, **kw):
        """Sets an item in the cache.  Returns True if the item was
        successfully added, or False if the cache params prevented this item
        being cached (eg, it is too big).
        """
        self.lock.acquire()
        try:
            try:
                return self.do_set(*args, **kw)
            except Uncachable:
                self.stats.add_uncachable()
                raise
        finally:
            self.lock.release()

    def _fetch_fresh(self, key):
        try:
            new_key, meta, data = self.provider.provide(key)
        except Uncachable:
            self.stats.add_uncachable()
            raise
        self.logger.debug("Cache provider provided '%s': %s", key, meta)
        if new_key != key:
            self.dispose(key)

        self.set(new_key, (meta, data))
        return meta, data

    def update_accessed_time(self, key, meta, now):
        if self.track_accessed:
            logger = self.logger
            meta.t_accessed = now
            # Must acquire the lock when updating the cache.
            self.lock.acquire()
            try:
                logger.debug("_get lock acquired for update of accessed time")
                # Check we actually still have the item - if another thread
                # removed it on us, we can't add it to the queue, else the
                # dequeue will fail to remove it!
                # This check is handled by update_meta, so attempt that
                # first.
                try:
                    self.data.update_meta(key, meta)
                    self.queue_accessed[key] = now
                    self.dirty = True
                except KeyError:
                    # Another thread has removed it from us - that's OK
                    pass
            finally:
                logger.debug("_get lock releasing for update of accessed time")
                self.lock.release()

    def validate_item(self, now, key, meta, data, validator = None, *args, **kw):
        logger = self.logger
        try:
            logger.info("Cache attempting validation for '%s'", key)
            logger.debug("Pre-validation metadata for '%s' is %s", key, meta)
            try:
                # XXX - we should add an assertion here that 'meta' isn't
                # changed by the validate function - for some caches its
                # actually the item in our cache, so changing it screws our
                # state.  (For disk cases - eg, EP - its not a real problem
                # as each 'self[foo]' returns a unique instance)
                if validator is None:
                    meta = self.provider.validate(key, meta, data, *args, **kw)
                else:
                    meta = validator(key, meta, data, *args, **kw)
            except ValidationGotNewItem, (new_key, meta, data):
                # The validation process said the old item was stale and gave
                # us a new one to use instead
                # (eg, If-Modified-Since request returned 200 instead of 304)
                logger.debug("validation of %r yielded a new item", new_key)
                if key != new_key:
                    self.dispose(key)

                self.set(new_key, (meta, data)) # may raise Uncachable
                return meta, data
        except Uncachable:
            self.stats.add_uncachable()
            raise
        except KeyError:
            # Validation failed - ask provider for a fresh copy.
            logger.info("Validation of '%s' failed - removing and refetching",key)
            self.dispose(key)
            return self._fetch_fresh(key)

        # Must acquire the lock when updating the cache.
        self.lock.acquire()
        try:
            logger.debug(
                "validate_item lock acquired for update of validated metadata")

            # Update the metadata for the validated item
            self.fixupMeta(meta, now) # includes t_accessed
            logger.debug("Post-validation metadata for key '%s' is %s", key, meta)
            try:
                self.data.update_meta(key, meta)
            except KeyError:
                # Another thread must have expired it - no problem.
                logger.info(
                    "key %r was expired before the meta could be updated", key)
        finally:
            logger.debug(
                "validate_item lock releasing for update of validated metadata")
            self.lock.release()

        return meta, data

    def is_item_fresh(self, meta, now):
        """ Does the cache consider the item 'fresh'?  This looks only at
        the cached response age etc - other app specific considerations
        (such as cache-control headers in a HTTP request, or 'Vary' headers
        in the cached entity) are not considered."""
        return now < meta.t_stale

    def _get(self, key, validator = None, *args, **kw):
        logger = self.logger
        logger.info("Cache request for key '%s'", key)
        lnow = now()
        try:
            meta, data = self.raw_get(key)
        except KeyError:
            logger.debug("Initial cache miss '%s'", key)
            return self._fetch_fresh(key)

        # check it is up-to-date
        is_fresh = self.is_item_fresh(meta, lnow)
        if not is_fresh:
            # this kinda sucks - a disconnect between the 'provider' and
            # 'storage'.  If the storage provided a file, we want to close it
            # ASAP, else a reference may be kept when a KeyError is thrown.
            try:
                data.close()
            except AttributeError:
                pass
            meta, data = self.validate_item(
                lnow, key, meta, data, validator, *args, **kw)
        else:
            # self._do_validation() will have updated
            # last_accessed for us - so we only need to update for a cache hit.
            self.update_accessed_time(key, meta, lnow)

        logger.info("Cache request for key '%s' was a hit", key)
        self.stats.add_hit(not is_fresh)
        return meta, data

    def get(self, key, validator = None, *args, **kw):
        meta, data = self._get(key, validator, *args, **kw)
        return data

    def getmeta(self, key, validator = None, *args, **kw):
        meta, data = self._get(key, validator, *args, **kw)
        return meta

    def raw_get(self, key):
        """ Get a value from the cache without any 'expired' or validation
        semantics. Raises KeyError, or returns meta, data """
        self.stats.add_get()

        # Must lock, even for a fetch!  Another thread (with the lock) may
        # be writing metadata for this very item, causing us to read garbage.
        self.lock.acquire()
        try:
            self.logger.debug("_get lock acquired")
            # make sure we are not currently purging it.
            if self.is_purge_pending(key):
                raise KeyError(key)
            meta, data = self.data[key]
            return meta, data
        finally:
            self.logger.debug("_get lock releasing")
            self.lock.release()

    def raw_query(self, *args, **kw):
        """ query storage, query is storage specific method """
        self.stats.add_get()

        # Must lock, even for a fetch!  Another thread (with the lock) may
        # be writing metadata for this very item, causing us to read garbage.
        self.lock.acquire()
        try:
            self.logger.debug("_get lock acquired")
            key, meta, data = self.data.query(*args, **kw)

            # make sure we are not currently purging it.
            if self.is_purge_pending(key):
                raise KeyError(key)

            return key, meta, data
        finally:
            self.logger.debug("_get lock releasing")
            self.lock.release()

    def __getitem__(self, key):
        return self._get(key)

    def __delitem__(self, key):
        self.dispose(key)

    def _purge_matches(self, purge_request, key):
        return key.startswith(purge_request)

    def is_purge_pending(self, key):
        for p in self.data.purge_iter():
            if self._purge_matches(p, key):
                return True
        return False

    def purge_startswith(self, key):
        self.lock.acquire()
        try:
            if self._purge_event is None:
                raise RuntimeError, "this cache not setup for purging."

            for p in self.data.purge_iter():
                if key == p:
                    # already in the list - nothing to do - but for the
                    # sake of ensuring the queue is still getting processed,
                    # set the event.
                    self._purge_event.set()
                    return
            self.data.purge_add(key)
            # wake the purge thread.
            self._purge_event.set()
        finally:
            self.lock.release()

    def _purge_thread_function(self):
        logger = self.logger
        logger.debug("Purge thread starting")
        while 1:
            self._purge_event.wait()
            self._purge_event.clear()
            logger.debug("Purge thread woken")
            while 1:
                self.lock.acquire()
                try:
                    logger.debug("Purge thread looping")
                    if self.data is None:
                        break # cache is closing
                    finished = False
                    for item in self.data.purge_iter():
                        for k in self.data.iterkeys(item):
                            if not self._purge_matches(item, k):
                                # finished purging this item - remove it
                                finished = True
                                break
                            self.dispose(k)
                            logger.debug("Purge of %r deleted %r", item, k)
                            break # only 1 at a time
                        else:
                            # no items in the iterator - also finished
                            finished = True

                        if finished:
                            self.data.purge_remove(item)
                            logger.debug("Purge of key %r complete", item)
                        # only do one at a time
                        break
                    else:
                        # no items left; break out and wait for new request.
                        break
                finally:
                    self.lock.release()
            if self.data is None:
                break # cache is closing

        logger.debug("Purge thread finishing")

    def _iter_problems(self):
        calcd_size = 0
        for key in self.data.iterkeys():
            # must use raw-get to avoid the validation process - we don't
            # care if its stale or not!
            meta, data = self.raw_get(key)
            if hasattr(data, "readlines"):
                data_len = 0
                for l in data.readlines():
                    data_len += len(l)
            else:
                data_len = len(data)
            if data_len != meta.size:
                yield (key, "meta_data has size of %d, but data is actually %d"
                       % (meta.size, data_len))

            calcd_size += meta.size

        if calcd_size != self.size:
            yield (None, "Calculated size is %d, but cache thinks it is %d"
                   % (calcd_size, self.size))

    def _check(self):
        """A debugging utility to check if a cache is inconsistent.  It should
        never be.  This may take a long time to execute as it walks the entire
        cache.  It should not be used while the cache is being used or it will
        report false positives.  Raises an AssertionError on failure, with the
        arg being a list of [key, problem], where key may be None if it applies
        to the cache itself.
        """
        self.maintain()
        problems = list(self._iter_problems())
        if problems:
            raise AssertionError(problems)
