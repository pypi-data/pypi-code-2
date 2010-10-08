################################################################################
# Copyright: Enfold Systems, LLC
# $Id: httpcache.py 4292 2010-08-30 19:57:37Z nikolay $
#
# A sample socket server that proxies some external site, but caches the content
#
# Todo:
# * We should reject all HTTP 1.0 clients and servers.
# * RFC2616 says we should add WARNING headers in some cases, and possibly
#   information about cache-hit
# * Handle content-type - we don't check the cached content-type is the
#   same as the request.
# * We cache all URLs, including those with authentication headers, cookies
#   and query fragments.  We shouldn't, unless explicit cache enableing
#   headers have been provided (says who?  Not the RFC :)
################################################################################

import datetime, base64
from cPickle import loads, dumps
from bsddb.dbutils import DeadlockWrap

from enfold.gcache.cache import metadata
from enfold.gcache.diskstorage import DiskStorage
from enfold.gcache.httpcacheprovider import HTTPCacheProvider
from enfold.gcache import utils
from enfold.gcache.utils import calc_age, delta_to_seconds, \
    get_time_header, get_time_value, get_if_modified_since, \
    iter_name_value_pairs
from enfold.gcache.interfaces import Uncachable


class httpmetadata(metadata):
    # NOTE about the metadata slots we inherit:
    # * t_modified is the date the item was added to the cache - it is
    #   *not* related to the "Last-Modified" header in a http request.
    # * t_verified is the date the item was most recently validated. Thus,
    #   t_verified can be considered the "request_time" used by the RFC (ie,
    #   "the (local) time when the cache made the request that resulted in
    #   this cached response"
    __slots__ = metadata.__slots__ + (
        # meta_headers is a dict, keyed by the hash of the lower-case header
        # (to keep the pickle size down; we never need to iterate over the
        # keys), with value a tuple of (literal, parsed) where literal is the
        # literal string value of the header, parsed is the parsed value (eg,
        # datetime object, integer) or None if that doesn't make sense.
        #
        # Each validation request, the server generally returns some updated
        # header values (eg, Date, Expires, cache-control). By storing
        # the updated values in meta_headers, we can avoid needing to replace
        # the cache *data* each validation (ie, the headers in the stored file
        # are always what came with the *initial* request, not subsequent
        # ones.) These are setup as an item is created, so they are always
        # valid. (ie, if the item has never been validated, meta_headers will
        # always reflect the stored message) Note that not all headers are
        # stored - only the ones the RFC says are OK, plus a couple to help
        # our impl (eg, last-modified, etag)
        'meta_headers',
        # if there is an error validating a stale response, can we use it
        # anyway? Default is True, but Cache-Control with "must-revalidate"
        # sets this to False.
        'stale_ok_on_error',
    )

    # The names of headers that a validate request may possibly update.  In
    # other words, a list of headers that we trust self.meta_headers over the
    # data stored in the initial cached response.  The type is the parsing
    # that should be done.
    # RFC sect. 10.3.5 lists "Expires, Cache-Control, and/or Vary"
    validate_volatile_headers  = [("date", datetime.datetime),
                                  ("expires", datetime.datetime),
                                  ("cache-control", tuple),
                                  ]

    def __init__(self, response, request_time, now, logger):
        super(httpmetadata, self).__init__(-1, None)

        self.meta_headers = {}
        self.stale_ok_on_error = False
        self.update_from_response(response, request_time, now, logger)

    def get_meta_header(self, hdr):
        """ Get a header value from self.meta_headers.  The list of headers is
        fixed, so it is an error to request a header that doesn't exist
        (although its not an error for the header value to be None, meaning
        it was not in the most recent request.)"""
        return self.meta_headers[hash(hdr)]

    def update_from_response(self, response, request_time, now, logger):
        """ Update metadata from a response - either the first reponse, or
        a validation response.
        Note: gcache is very much "now" based, where HTTP caching tends to
        be relative to the response date. RFC2616 spells out the definition
        of "age" and "freshness", so we first calculate these values, then
        convert them to values suitable for the cache."""
        is_update = len(self.meta_headers) != 0

        msg = response.msg

        date = get_time_header(msg, "Date", logger)
        if date is None:
            logger.debug("No date in response - assuming now")
            date = now

        # its not clear 'age' here is sane :(
        try:
            age = datetime.timedelta(seconds=int(msg.get("Age", 0)))
        except (ValueError, TypeError):
            age = utils.timedeltazero

        # stash the headers we care about away
        meta_headers = self.validate_volatile_headers + \
                       [("last-modified", datetime.datetime)]

        # Setup our 'meta-headers' early as we rely on them later in this method.
        for hdr_name, hdr_type in meta_headers:
            val = msg.get(hdr_name)
            # Very first time we must set the value, even if None.  Subsequent
            # updates must *not* update the value if the new value is None as
            # the old value remains valid.
            if not is_update or val is not None:
                if val is None or hdr_type is None:
                    parsed = None
                elif hdr_type is datetime.datetime:
                    parsed = get_time_value(val)
                elif hdr_type is tuple:
                    # comma-sep'd values
                    parsed = list(iter_name_value_pairs(val))

                self.meta_headers[hash(hdr_name)] = (val, parsed)

        # RFC2616, Section 13.2.3 Age Calculations:
        # We assume we only just got the response - so response_time==now.
        current_age = calc_age(age, date, request_time, now, now)

        # RFC2616, Section 13.2.4 Expiration Calculations
        # First look at the headers which tell us the info.
        self.stale_ok_on_error = True
        max_age = None
        max_age_trumped = False # s-maxage wins!
        cant_cache_reason = None

        # Some of these can be on either the request or the response - we
        # are only looking at the response from the origin server here.  See
        # self.fresh_for_request() for the request handling.
        #RFC lists the following 'cache-response-directive's:
        # | "public"                               ; Section 14.9.1
        # | "private" [ "=" <"> 1#field-name <"> ] ; Section 14.9.1
        # | "no-cache" [ "=" <"> 1#field-name <"> ]; Section 14.9.1
        # | "no-store"                             ; Section 14.9.2
        # | "no-transform"                         ; Section 14.9.5
        # | "must-revalidate"                      ; Section 14.9.4
        # | "proxy-revalidate"                     ; Section 14.9.4
        # | "max-age" "=" delta-seconds            ; Section 14.9.3
        # | "s-maxage" "=" delta-seconds           ; Section 14.9.3
        # | cache-extension

        # We can use the 'parsed' cache-control header values directly
        ok_when_authed = False
        cc_items = self.get_meta_header('cache-control')[1] or [] # may be none
        for v, val in cc_items:
            logger.debug("Cache-Control: %s=%s", v, val)

            if v in ("private", "no-store"):
                cant_cache_reason = "Cache-Control: private or no-store"
                # XXX: todo: look at possible field names in 'private'

            elif v == "no-cache":
                if val:
                    # a header was specified - that means we are free to keep
                    # the cached response, but can't store the header.
                    pass # we check that later!
                else:
                    # RFC says "then a cache MUST NOT use the response
                    # to satisfy a subsequent request without
                    # successful revalidation with the origin server."
                    # So we just set the stale time to now, forcing a
                    # revalidate.
                    # XXX: todo: look at possible field names...
                    max_age = 0

            elif v in ("must-revalidate", "proxy-revalidate"):
                self.stale_ok_on_error = False
                ok_when_authed = True

            elif v.startswith("s-maxage"):
                try:
                    max_age = int(val)
                except (ValueError, TypeError):
                    cant_cache_reason = "Invalid s-maxage value %r" % (val,)
                    break
                # RFC sez "The s-maxage directive also implies the
                # semantics of the proxy-revalidate directive"
                self.stale_ok_on_error = False
                max_age_trumped = True # prevent 'max-age' from overriding us
                ok_when_authed = True

            elif v.startswith("max-age"):
                if max_age_trumped:
                    continue
                try:
                    max_age = int(val)
                except (ValueError, TypeError):
                    cant_cache_reason = "Invalid max-age value %r" % (val,)
                    break

            elif v == "public":
                ok_when_authed = True

        if not ok_when_authed:
            # yuck: we don't really allow apps to override this class, so
            # a 'self.is_response_authorized' method doesn't work.  So
            # if someone wants to override this (eg, to allow certain cookies
            # to be considered as 'authorized', they must monkey-patch the
            # response object.
            try:
                is_authed = response.is_authorized()
            except AttributeError:
                # default is to stick to rfc2616
                is_authed = "authorization" in response.msg

            if is_authed:
                raise Uncachable(
                    "Response is authorized and not explicitly public")

        expires = get_time_header(msg, "Expires", logger=logger)
        if expires is not None and max_age is None:
            last_modified = get_time_header(msg, "Last-Modified", logger=logger)
            if last_modified is not None and last_modified > expires:
                raise Uncachable(
                    "Response's Last-Modified is geater than Expires")

        # Now calculate the times and other metadata for the cache.
        t_verified = now
        if max_age is None:
            if expires is None:
                # indicate the cache can use its default behaviour.
                t_stale = None
            else:
                t_stale = expires # in the past is OK
        else:
            freshness_lifetime = datetime.timedelta(seconds=max_age)
            # negative max_age is not OK
            freshness_lifetime = max(utils.timedeltazero, freshness_lifetime)
            # response_is_fresh = (freshness_lifetime > current_age)
            t_stale = t_verified + freshness_lifetime - current_age

        try:
            size = int(msg["Content-Length"])
        except (KeyError, ValueError, TypeError):
            # response may be chunked and missing a content-length - use -1
            # to record 'don't know yet' vs 'zero byte response'
            size = -1

        # If a non-200 has an explicit cache directive, it can be cached.
        # We never validate non-200 responses, so it must also be 'fresh'
        if response.status != 200:
            if t_stale is None or t_stale <= now:
                cant_cache_reason = \
                    "non-200 status (%s: %s) with no cache headers" \
                    % (response.status, response.reason)

        if cant_cache_reason is not None:
            raise Uncachable, "Response includes %s" % (cant_cache_reason,)

        self.size = size
        self.t_stale = t_stale
        self.t_verified = t_verified
        if self.t_modified is None:
            self.t_modified = t_verified

    def fixup_response_headers(self, msg, logger=None):
        """Fixup the headers that are about to be returned to the client
        to reflect the state of the cached item we are serving"""
        now = utils.now()

        # Currently this means the values in validate_volatile_headers, plus
        # the "Age" header.
        for hdr_name, hdr_type in self.validate_volatile_headers:
            new_raw, new_parsed = self.get_meta_header(hdr_name)
            # If the most recent entry is None, then the value in the
            # initial request, if any, remains.
            if new_raw is not None:
                msg[hdr_name] = new_raw

        date = get_time_header(msg, "Date", logger)
        if date is None:
            date = now

        # A value for age.
        try:
            age = datetime.timedelta(seconds=int(msg.get("Age", 0)))
        except (ValueError, TypeError):
            age = utils.timedeltazero

        # the request time is t_verified in our meta, and we don't keep the
        # request delay :()
        current_age = calc_age(age, date, self.t_verified, self.t_verified, now)
        msg['Age'] = str(delta_to_seconds(current_age))

    def conditional_request_matches(self, req_headers, cached_msg, logger):
        """ Does this cached item match a 'conditional' request for the item?
        ie, can we return a 304.  req_headers are from the client, cached_msg
        is from what we already have parsed from our cached data file. """

        resp_lm_raw, resp_lm_date = self.get_meta_header("last-modified")

        # If-Modified-Since
        ims, ims_len = get_if_modified_since(req_headers, logger)
        if ims is not None and resp_lm_date:
            # if len fails to match bail early
            if ims_len is not None and \
                    str(ims_len) != cached_msg.get("Content-Length", 0):
                return False

            if resp_lm_raw == ims: # exact string match
                return True

            # Maybe its a date?
            ims_date = get_time_value(ims)
            if ims_date is not None and resp_lm_date <= ims_date:
                return True

        elif req_headers.get('IF-None-Match') and not resp_lm_date:
            # with ETag and without Last-Modified
            return True

        # XXX - other 'if-xxx' tests.
        return False

    def fresh_for_request(self, now, cached_headers, req_headers, logger):
        """ Checks the freshness of a cache entry against a client
        request, which may specify additional constraints.
        In this context, 'freshness' simply means 'do I need to revalidate'.
        cached_headers are the headers as read from the cached file
        req_headers are the client request headers """

        # cache-control header first.
        saw_max_stale = False
        cc = req_headers.get("cache-control")
        if cc:
            for v, val in iter_name_value_pairs(cc):
                saw_max_stale = saw_max_stale or v=='max-stale'
                if not self._check_cachecontrol_header(v, val, now, logger):
                    logger.debug(
                        'fresh_for_request is stale (Cache-Control: %s=%s)',
                        v, val)
                    return False

        # Unless we saw a max-stale directive, the cache itself still gets
        # to control the validity of the expiry time
        if not saw_max_stale and now > self.t_stale:
            logger.debug('fresh_for_request is stale (cache expiry)')
            return False

        logger.debug('fresh_for_request is fresh')
        return True

    def _check_cachecontrol_header(self, v, val, now, logger):
        # RFC2616 lists the following cache-control params the client may send:
        # cache-request-directive =
        #  | "no-cache"                          ; Section 14.9.1
        #  | "no-store"                          ; Section 14.9.2
        #  | "max-age" "=" delta-seconds         ; Section 14.9.3, 14.9.4
        #  | "max-stale" [ "=" delta-seconds ]   ; Section 14.9.3
        #  | "min-fresh" "=" delta-seconds       ; Section 14.9.3
        #  | "no-transform"                      ; Section 14.9.5
        #  | "only-if-cached"                    ; Section 14.9.4
        #  | cache-extension                     ; Section 14.9.6

        if v == 'no-cache':
            # Client included no-cache - this means that the response MUST
            # be revalidated before use, regardless of age.
            return False

        # 'no-store' isn't relevant here - it reflects if we can store a new
        # response.
        if v == 'max-age':
            # Note: RFC says if cached entry and request both specify max-age,
            # then smallest is used. max-age on the cached request is
            # reflected on our metadata - so we just check if expired by our
            # expiry first, then by the client-request.
            if now >= self.t_stale:
                return False

            # Fresh enough in the cache - check the client constraints.
            try:
                max_age = datetime.timedelta(seconds=int(val))
            except (ValueError, TypeError):
                logger.warning('invalid integer param in %r', val)
                return True
            return (now - self.t_verified) <= max_age

        # max-stale: Response that has exceeded its expiration time by no more
        # than the specified number of seconds
        if v == 'max-stale':
            try:
                max_stale = datetime.timedelta(seconds=int(val))
            except (ValueError, TypeError):
                logger.warning('invalid integer param in %r', val)
                return True
            return (now - self.t_stale) <= max_stale

        # min-fresh: freshness lifetime is no less than its current age plus
        # the specified time in seconds.
        if v == 'min-fresh':
            try:
                min_fresh = datetime.timedelta(seconds=int(val))
            except (ValueError, TypeError):
                logger.warning('invalid integer param in %r', val)
                return True
            return now + min_fresh < self.t_stale

        return True


class Storage(DiskStorage):

    def _load_(self, fp):
        return fp.read()

    def _dump_(self, data, fp):
        fp.write(data)

    def _etag_key(self, url, request_headers):
        key = [url]

        # etag
        etag = request_headers.get('IF-None-Match', '')
        if etag.startswith('W'):
            etag = etag[2:]

        if etag:
            key.append(base64.b64encode(etag))
        else:
            key.append('*')

        key.append('')
        return '|'.join(key)

    def query(self, url, request):
        """ query meta by request """
        cursor = self.data.cursor()

        ekey = self._etag_key(url, request)
        ekey_len = len(ekey)

        self.logger.log(1, "Loading %r metadata from DB", ekey)

        got = cursor.set_range(ekey)
        while got:
            # check if we miss strong key
            if not got[0].startswith(ekey):
                cursor.close()
                raise KeyError(ekey)

            key, data = got

            vary = key[ekey_len:]
            if vary == '~':
                vary = {}
            else:
                vary = loads(base64.b64decode(vary))

                matched = True
                for hdr, val in vary.items():
                    if request.get(hdr, '').strip() != val:
                        matched = False
                        break

                if not matched:
                    got = cursor.next()
                    continue

            cursor.close()

            meta = loads(got[1])[0]
            fname = self._get_filename(key, meta)
            try:
                fp = open(fname, "rb")
                if self.return_files:
                    data = fp
                else:
                    data = self._load_(fp)
                    fp.close()
            except EnvironmentError, details:
                self.logger.error(
                    "Failed to read cache-file '%s' - %s", fname, details)
                raise KeyError(key)

            self.logger.log(1, "Load complete")
            return key, meta, data

        cursor.close()
        raise KeyError(ekey)

    def del_url(self, cache, url):
        """ remove all keys for url """
        self._del_keys(cache, '%s|'%url)

    def del_keys(self, cache, url, request):
        """ delete keys that are generated from request """
        self._del_keys(cache, self._etag_key(url, request))

    def _del_keys(self, cache, basekey):
        # remove all keys
        cursor = self.data.cursor()
        got = cursor.set_range(basekey)

        keys = []
        while got:
            if not got[0].startswith(basekey):
                break

            keys.append(got[0])
            got = cursor.next()

        cursor.close()
        for key in keys:
            cache.dispose(key)


class CacheProvider(HTTPCacheProvider):

    metadataFactory = httpmetadata
