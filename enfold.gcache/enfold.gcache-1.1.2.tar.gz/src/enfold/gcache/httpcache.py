################################################################################
# Copyright: Enfold Systems, LLC
# $Id: httpcache.py 4414 2010-10-08 15:24:18Z nikolay $
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

import os, sys, time
import re
import httplib
import socket
import datetime
import dateutil.parser, dateutil.tz

from enfold.gcache import Cache, metadata, getLogger, now
from enfold.gcache import Uncachable, ValidationGotNewItem
from enfold.gcache import DiskStorage

HEADERS_LOG_LEVEL = 13 # Nod to EP - this is the level is uses for headers.

now_func = now # now is commonly shadowed!

# from rfc2616, section 13.5.1
hop_by_hop_headers = set(('connection', 'keep-alive', 'proxy-authenticate',
                          'proxy-authorization', 'te', 'trailers',
                          'transfer-encoding', 'upgrade'))

# Optional length (hrmph - where did this come from?  RRC2616 doesn't seem to
# mention it, our tests don't hit it, and the impl was wrong (we previously
# checked for a content-length in the *client* request!)
re_ims_value = re.compile("([^;]+)((; length=([0-9]+)$)|$)")

# Expose 'parse_date' and 'format_date' functions to hide the implementation.
parse_date = dateutil.parser.parse

# Save creating lots of temp objects.
timedeltazero = datetime.timedelta()


def delta_to_seconds(delta):
    ret = delta.days * 86400 + delta.seconds
    if delta.microseconds >= 500000:
        ret += 1
    return ret


def calc_age(age_value, date_value, request_time, response_time, now=None):
    # From http://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html
    # Section 13.2.3 - age
    #* age_value
    #*      is the value of Age: header received by the cache with
    #*              this response.
    #* date_value
    #*      is the value of the origin server's Date: header
    #* request_time
    #*      is the (local) time when the cache made the request
    #*              that resulted in this cached response
    #* response_time
    #*      is the (local) time when the cache received the
    #*              response
    #* now
    #*      is the current (local) time
    if now is None:
        now = now_func()
    apparent_age = max(timedeltazero, response_time - date_value)
    corrected_received_age = max(apparent_age, age_value)
    response_delay = response_time - request_time
    corrected_initial_age = corrected_received_age + response_delay
    resident_time = now - response_time
    current_age   = corrected_initial_age + resident_time
    return current_age


def get_time_header(msg,name, default=None, logger=None):
    val = msg.get(name)
    if not val: return default
    return get_time_value(val, default, logger)


def get_time_value(val, default=None, logger=None):
    try:
        return parse_date(val)
    except ValueError:
        (logger or getLogger()).warning("Failed to parse date value '%s'", val)
        return default


# Parse an 'If-Modified-Since: date[;length=nnn]' header.  Return the raw date
# so we can string compare without parsing as an optimization.
# See above though - where does the length=xxx thing come from???
def get_if_modified_since(msg, logger=None):
    val = msg.get("If-Modified-Since")
    if not val:
        return None, None

    m = re_ims_value.match(val)
    if not m:
        return None, None

    try:
        date = m.group(1)
        size = m.group(4)
        if size is not None:
            size = int(size)
    except (ValueError, TypeError):
        (logger or getLogger()).exception(
            "Failed to parse 'If-Modified-Since: %s'", val)
        return None, None
    return date, size


def iter_header_values(header_val):
    # Given the value of a header, return a generator which cracks all the
    # lower-case values
    if not header_val:
        return
    for bit in header_val.split(","):
        yield bit.strip().lower()


def iter_name_value_pairs(header_val):
    # Given the value of a Cache-Control (or similar) header, return a
    # generator which cracks all the vlaues - lower-case keys and anything
    # after the '=' as a value (or None if no =)
    if not header_val:
        return
    for bit in iter_header_values(header_val):
        if '=' in bit:
            v, val = bit.split("=", 1)
        else:
            v = bit
            val = None
        yield v, val


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
        # header values (eg, Date, Expires, cache-control, Vary). By storing
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
                                  ("vary", None),
                                  ("cache-control", tuple),
                                  ]

    def __init__(self, response, request_time, now=None, logger=None):
        self.meta_headers = {}
        self.stale_ok_on_error = False # conservative default, always overridden
        # base __init__ is light-weight - get that out of the way now -
        # real values will be updated in update_from_response
        metadata.__init__(self, -1, None)
        self.update_from_response(response, request_time,now=now,logger=logger)

    def get_meta_header(self, hdr):
        # Get a header value from self.meta_headers.  The list of headers is
        # fixed, so it is an error to request a header that doesn't exist
        # (although its not an error for the header value to be None, meaning
        # it was not in the most recent request.)
        # NOTE: Later we are likely to need to loosen this restriction to
        # support 'Vary', which means arbitrary headers will be needed
        assert hdr.lower() == hdr, "only pass lowercase literals please."
        return self.meta_headers[hash(hdr)]

    def update_from_response(self, response, request_time,now=None,logger=None):
        # Update metadata from a response - either the first reponse, or
        # a validation response.
        # Note: gcache is very much "now" based, where HTTP caching tends to
        # be relative to the response date. RFC2616 spells out the definition
        # of "age" and "freshness", so we first calculate these values, then
        # convert them to values suitable for the cache.
        is_update = len(self.meta_headers) != 0

        if now is None:
            now = now_func()

        # request_time is when we started the request for the response
        # resulting in us being here.  Thus, it is just a measure of network
        # latency and Zope's overhead - it should be very close to now - so
        # sanity check it.
        assert now-request_time < datetime.timedelta(seconds=5), \
               "insane request time? request was at %s, but now is %s (%s)" \
               % (request_time, now, now-request_time)

        msg = response.msg

        # metadata is pickled etc - that makes it a PITA to have
        # self.logger work :(
        logger = logger or getLogger()

        date = get_time_header(msg, "Date", logger=logger)
        if date is None:
            logger.debug("No date in response - assuming now")
            date = now

        # its not clear 'age' here is sane :(
        try:
            age = datetime.timedelta(seconds=int(msg.get("Age", 0)))
        except (ValueError, TypeError):
            age = timedeltazero

        # stash the headers we care about away
        meta_headers = self.validate_volatile_headers + \
                       [("last-modified", datetime.datetime),
                        ("etag", None),
                       ]

        # Setup our 'meta-headers' early as we rely on them later in this
        # method.
        # NOTE: The above will fail in the future when we beef up Vary support
        # - that will require us to store arbitrary headers (those listed in
        # Vary)
        assert len(self.meta_headers) in [0, len(meta_headers)], \
               "There is an extra meta-header here I'm not expecting\n%r" % (
            self.meta_headers,)

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
                #elif hdr_type is int:
                #    try:
                #        parsed = int(val)
                #    except (ValueError, TypeError):
                #        logger.warning(
                #            "Invalid integer value %s: %s", hdr_name, val)
                #        parsed = None
                elif hdr_type is tuple:
                    # comma-sep'd values
                    parsed = list(iter_name_value_pairs(val))
                else:
                    raise ValueError, "unknown type %s" % (hdr_type,)

                assert hdr_name.lower() == hdr_name, \
                    "these constants must be lower"
                self.meta_headers[hash(hdr_name)] = (val, parsed)

        # RFC2616, Section 13.2.3 Age Calculations:
        # We assume we only just got the response - so response_time==now.
        current_age = calc_age(age, date, request_time, now)

        # RFC2616, Section 13.2.4 Expiration Calculations
        # First look at the headers which tell us the info.
        self.stale_ok_on_error = True
        max_age = None
        max_age_trumped = False # s-maxage wins!
        cant_cache_reason = None

        # Handle possible HTTP 1.0 cache-control header.
        # XXX - we assume a http 1.1 server, so this should not exist.  It is
        # in the client request headers this is more likely...  But we don't
        # currently check the server version, so it stays for now...
        for v in msg.getheaders("Pragma"):
            if v.lower()=="no-cache":
                max_age = 0

        # Some of these can be on either the request or the response - we
        # are only looking at the response from the origin server here.  See
        # self.fresh_for_request() for the request handling.
        #RFC lists the following 'cache-response-directive's:
        #   "public"                               ; Section 14.9.1
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
            freshness_lifetime = max(timedeltazero, freshness_lifetime)
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
        self.t_verified = t_verified
        if self.t_modified is None:
            self.t_modified = t_verified
        self.t_stale = t_stale

    def fixup_response_headers(self, msg, logger=None):
        """Fixup the headers that are about to be returned to the client
        to reflect the state of the cached item we are serving"""
        # Currently this means the values in validate_volatile_headers, plus
        # the "Age" header.
        for hdr_name, hdr_type in self.validate_volatile_headers:
            new_raw, new_parsed = self.get_meta_header(hdr_name)
            # If the most recent entry is None, then the value in the
            # initial request, if any, remains.
            if new_raw is not None:
                msg[hdr_name] = new_raw

        date = get_time_header(msg, "Date", logger=logger)
        if date is None:
            date = now_func()

        # A value for age.
        try:
            age = datetime.timedelta(seconds=int(msg.get("Age", 0)))
        except (ValueError, TypeError):
            age = timedeltazero
        # the request time is t_verified in our meta, and we don't keep the
        # request delay :()
        current_age = calc_age(age, date, self.t_verified, self.t_verified)
        msg['Age'] = str(delta_to_seconds(current_age))

    # Does this cached item match a 'conditional' request for the item?
    # ie, can we return a 304.  req_headers are from the client, cached_msg
    # is from what we already have parsed from our cached data file.
    def conditional_request_matches(self, req_headers, cached_msg, logger=None):
        # ETag comparisons are 'strong', so must be done first.
        val = req_headers.get("If-None-Match")
        if val is not None:
            raw, parsed = self.get_meta_header("etag")
            if val == raw:
                return True

        # If-Modified-Since
        ims, ims_len = get_if_modified_since(req_headers, logger=logger)
        if ims is not None:
            # if len fails to match bail early
            if ims_len is not None and \
                    str(ims_len) != cached_msg.get("Content-Length", 0):
                return False
            resp_lm_raw, resp_lm_date = self.get_meta_header("last-modified")
            if resp_lm_raw == ims: # exact string match
                return True
            if not resp_lm_date:
                # we have no date in the cached copy!  Can't possibly match.
                return False
            # Maybe its a date?
            try:
                ims_date = parse_date(ims)
            except ValueError:
                ims_date = None
            try:
                if ims_date is not None and resp_lm_date <= ims_date:
                    return True
            except TypeError:
                # If somehow we didn't get a timezone in one of the dates, we
                # might see:
                # TypeError: can't compare offset-naive and 
                # offset-aware datetimes. eg, see issue PROXY-401
                pass

        # XXX - other 'if-xxx' tests.
        return False

    # Checks the freshness of a cache entry against a client
    # request, which may specify additional constraints.
    # In this context, 'freshness' simply means 'do I need to revalidate'.
    # Cache-control headers in the request are an obvious variable, but less
    # obvious is 'Vary' - if the vary headers fail to match, we can still ask
    # the server for validation - it may still respond that the cached
    # response is OK.
    # cached_headers are the headers as read from the cached file
    # req_headers are the client request headers
    def fresh_for_request(self, now, cached_headers, req_headers, logger=None):
        logger = logger or getLogger()

        # cache-control header first.
        saw_max_stale = False
        for v, val in iter_name_value_pairs(req_headers.get("cache-control")):
            saw_max_stale = saw_max_stale or v=='max-stale'
            if not self._check_cachecontrol_header(v, val, now, logger=logger):
                logger.debug(
                    'fresh_for_request is stale (Cache-Control: %s=%s)', v, val)
                return False

        # Unless we saw a max-stale directive, the cache itself still gets
        # to control the validity of the expiry time
        if not saw_max_stale and now >= self.t_stale:
            logger.debug('fresh_for_request is stale (cache expiry)')
            return False

        # check vary.
        for h in cached_headers.getheaders('vary'):
            for v in h.split(','):
                v = v.strip()
                if v == '*':
                    logger.debug('fresh_for_request is stale (Vary: *)')
                    return False
                if req_headers.get(v, '') != cached_headers.get(v, ''):
                    logger.debug('fresh_for_request is stale (Vary: %r)', v)
                    return False

        # if cache containes record with last-modified and cache-control
        # headers, but browser sends If-None-Matche this could mean
        # that previous response contained 'etag' and 'cache-control: private'
        val = req_headers.get("If-None-Match")
        if val is not None:
            raw, parsed = self.get_meta_header("etag")
            if val != raw:
                return False

        logger.debug('fresh_for_request is fresh')
        return True

    def _check_cachecontrol_header(self, v, val, now, logger):
        # RFC2616 lists the following cache-control params the client may send:
        #cache-request-directive =
        #           "no-cache"                          ; Section 14.9.1
        #         | "no-store"                          ; Section 14.9.2
        #         | "max-age" "=" delta-seconds         ; Section 14.9.3,14.9.4
        #         | "max-stale" [ "=" delta-seconds ]   ; Section 14.9.3
        #         | "min-fresh" "=" delta-seconds       ; Section 14.9.3
        #         | "no-transform"                      ; Section 14.9.5
        #         | "only-if-cached"                    ; Section 14.9.4
        #         | cache-extension                     ; Section 14.9.6
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


class CacheProviderBase(object):

    def __init__(self, logger = None):
        self.logger = logger or getLogger()

    def provide(self, key):
        raise NotImplementedError

    def validate(self, key, meta, data, *args):
        raise NotImplementedError

    def open_host(self, scheme, host, port=None):
        if scheme == 'http':
            return httplib.HTTPConnection(host, port)
        elif scheme == 'https':
            return httplib.HTTPSConnection(host, port)
        raise ValueError, 'only http or https supported'

    def done_with_host(self, connection, response):
        # response may be None, but connection will never be.
        if response is not None:
            response.close()
        connection.close()

    def host_failed(self, connection):
        raise

    def do_provide(self, host, url):
        resp = None
        c = self.open_host('http', host)
        try:
            try:
                request_time = now()
                c.putrequest("GET", url)
                c.endheaders()
                resp = c.getresponse()

                metadata, bits = get_response_meta_and_prefix(
                    resp, request_time, self.logger)
                bits.append('') # blank line after headers.
                bits.append(resp.read())
                # We keep more than just the content, 
                # so content-length doesn't help.
                data = "\r\n".join(bits)
                metadata.size = len(data)
                return metadata, data
            except:
                self.host_failed(c)
        finally:
            self.done_with_host(c, resp)

    def do_validate(self, scheme, host, url, meta, data, request_headers=None):
        logger = self.logger
        # XXX - we also need to get a little smarter re fully-qualified-URLs etc
        if not isinstance(data, str):
            # must be a file, but we can't make assumptions about where the
            # pointer is, and we must leave it back where it was when done.
            existing = data.tell()
            data.seek(0,0)
            try:
                first_bit = data.readline()
            finally:
                data.seek(existing, 0)
        else:
            first_bit = data
        if not first_bit.startswith("200"):
            logger.debug("Can't validate non-200 responses")
            raise KeyError

        etag, _ = meta.get_meta_header('etag')
        server_modified, _ = meta.get_meta_header('last-modified')
        if not etag and not server_modified:
            logger.debug("Can't revalidate '%s/%s' - no Last-Modified or ETag",
                         host, url)
            raise KeyError
        if type(host) == type(()):
            host, port = host
        else:
            port = None
        resp = None
        c = self.open_host(scheme, host, port)
        try: # done_with_host
            try: # host_failed
                request_time = now()
                c.putrequest("GET", url)
                # rfc sect 13.6 says "[if vary doesn't match] then the cache
                # MUST NOT use a cached entry to satisfy the request unless it
                # first relays the new request to the origin server in a
                # conditional request"
                # ie, the *entire* set of client headers should be sent. This
                # is also necessary to make sense of 'Vary: *'
                if request_headers is not None and meta.get_meta_header('vary'):
                    for header_name in request_headers.keys():
                        vals = request_headers.getheaders(header_name)
                        c.putheader(header_name, ",".join(vals))

                if etag and (not request_headers or 'if-none-match' \
                                 not in request_headers):
                    c.putheader("If-None-Match", etag)
                    logger.debug("Adding header If-None-Match: %s", etag)
                if server_modified and (not request_headers or 
                                        'if-modified-since' not in 
                                        request_headers):
                    # RFC says we should pass back exactly what the server said,
                    # so we don't convert to/from a time value
                    c.putheader("If-Modified-Since", server_modified)
                    logger.debug("Adding header If-Modified-Since: %s",
                                 server_modified)

                c.endheaders()
                resp = c.getresponse()
                # Anything other than 200 or 304 is thrown away
                # again
                logger.info("Validate response %s: %s (%s)",
                            resp.status, resp.reason, url)
                # We do the same as EP does here
                if logger.isEnabledFor(HEADERS_LOG_LEVEL):
                    hdrs_output = "\n<-- ".join(
                        [h_.rstrip() for h_ in resp.msg.headers])
                    logger.log(HEADERS_LOG_LEVEL,
                               "Validate response headers\n<-- %s", hdrs_output)

                if resp.status == 200:
                    metadata, bits = get_response_meta_and_prefix(resp,
                                                                  request_time,
                                                                  logger)
                    bits.append('') # blank line after headers.
                    bits.append(resp.read())
                    # We keep more than just the content, 
                    # so content-length doesn't help.
                    data = "\r\n".join(bits)
                    metadata.size = len(data)
                    raise ValidationGotNewItem(metadata, data)
                if resp.status!=304:
                    raise KeyError

                # validate responses may or may not include the (hopefully same)
                # etag and last-modified - but that works OK as they are stored
                # as 'meta headers'.
                # According to the RFC, Content-Length MUST be supplied if it
                # would be for a normal 200 response - which means that an item
                # which would have come 'chunked' in a 200 need not supply the
                # content-length in a 304. If there isn't a metadata value of
                # '-1' will result, screwing our cache 'size' logic.
                old_size = meta.size
                resp.status = 200 # update_from_response checks this...
                meta.update_from_response(resp, request_time, logger=logger)
                if meta.size == -1: # no content-length supplied
                    meta.size = old_size
                elif meta.size != old_size:
                    logger.info(
                        "Ignoring 304 validation response with incorrect"
                        " content-length (old size %s, new size %s)",
                        old_size, meta.size)
                    raise KeyError
                # metadata looks good so we are happy.
                return meta
            except (socket.error, httplib.error):
                self.host_failed(c)
                # Note: socket or httplib errors here 
                # should be caught by the caller.
                # We do *not* want to flag the item as stale simply because the
                # origin site is down - the caller has a better idea than 
                # us about what the 'right thing' to do is there...
                # so throw it back up
                raise
        finally:
            self.done_with_host(c, resp)


def get_response_meta_and_prefix(response, request_time, logger):
    # returns metadata and the response headers that should be cached, given
    # a http response.
    assert response is not None, "don't call me without a valid response!"
    assert logger is not None, "don't call me without a valid logger!"
    metadata = httpmetadata(response, request_time, logger=logger)

    # RFC2616 defines "hop-by-hop" headers, which are ones we should remove,
    # but note that Cookies and auth headers are *not* in this list (but it
    # appears to allow the response itself to nominate other hop-by-hop headers
    # in the 'Connection' header.
    # Also, cache-control: no-cache=foo can be treated in exactly the same
    # way, as both have the nett result of removing the header from the
    # cache
    exclude_headers = hop_by_hop_headers.copy()
    conn = response.msg.get('connection')
    msg = response.msg
    if conn:
        for h in iter_header_values(conn):
            h = h.lower()
            if h != "close":
                exclude_headers.add(h)
    cc_exclude_seen = False
    cc = msg.get('cache-control')
    if cc:
        for h, v in iter_name_value_pairs(cc):
            if h=="no-cache" and v:
                exclude_headers.add(v)
                cc_exclude_seen = True
    # Nod to zope - no cache-control:no-cache header, we default to set-cookie
    if not cc_exclude_seen:
        exclude_headers.add('set-cookie')

    bits = ['%s %s' % (response.status, response.reason)]
    for h in iter(msg): # no iteritems :()
        if h.lower() not in exclude_headers:
            bits.append("%s: %s" % (h, msg[h]))
    return metadata, bits


# A cache provider that serves a single host, and uses the URL directly
# as a key.
class CacheProvider(CacheProviderBase):

    def __init__(self, host, logger = None):
        self.host = host
        CacheProviderBase.__init__(self, logger)

    def validate(self, key, meta, data, *args):
        return self.do_validate('http', self.host, key, meta, data, *args)

    def provide(self, key):
        return self.do_provide(self.host, key)
