################################################################################
#
# Copyright (c) 2010 Enfold Systems, LLC
# All Rights Reserved.
#
# http utils
#
# $Id:  2007-12-12 12:27:02Z fafhrd $
#
################################################################################

import re, datetime
from dateutil.tz import tzutc
from dateutil.parser import parse
from interfaces import HEADERS_LOG_LEVEL

timedeltazero = datetime.timedelta()


def now(tz=tzutc()):
    return datetime.datetime.now(tz)


def fixupTimeDelta(delta):
    if delta is not None and not isinstance(delta, datetime.timedelta):
        delta = datetime.timedelta(seconds=delta)
    return delta


# from rfc2616, section 13.5.1
hop_by_hop_headers = ('connection', 'keep-alive', 'proxy-authenticate',
                      'proxy-authorization', 'te', 'trailers',
                      'transfer-encoding', 'upgrade')


HEADERS_LOG_LEVEL = 13 # Nod to EP - this is the level is uses for headers.


def log_headers(logger, response, msg):
    if logger.isEnabledFor(HEADERS_LOG_LEVEL):
        hdrs_output = "\n<-- ".join(
            [h.rstrip() for h in response.msg.headers])
        logger.log(HEADERS_LOG_LEVEL, "%s: \n<-- %s", msg, hdrs_output)


def delta_to_seconds(delta):
    ret = delta.days * 86400 + delta.seconds
    if delta.microseconds >= 500000:
        ret += 1
    return ret


def get_time_value(val, default=None, tz=tzutc()):
    """ if parsed value does not contain time zone, set timezone to utc
    >>> get_time_value("Mon, 09 Aug 2010 16:48:45 GMT+5")
    datetime.datetime(2010, 8, 9, 16, 48, 45, tzinfo=tzoffset(None, -18000))

    >>> get_time_value("Mon, 09 Aug 2010 16:48:45")
    datetime.datetime(2010, 8, 9, 16, 48, 45, tzinfo=tzutc())
    """
    try:
        value = parse(val)
        if value.tzinfo is None:
            value = datetime.datetime(
                value.year, value.month, value.day,
                value.hour, value.minute, value.second, value.microsecond, tz)
        return value
    except ValueError:
        return default


def get_time_header(msg, name, logger=None, default=None):
    """ get value from message and parse it to datetime

    >>> import rfc822
    >>> from logging import getLogger
    >>> from StringIO import StringIO
    >>> log = getLogger()
    >>> headers = "Last-Modified:  Mon, 09 Aug 2010 16:48:45 GMT\\r\\n\\r\\n"

    >>> get_time_header(rfc822.Message(StringIO(headers)), 'last-modified', log)
    datetime.datetime(2010, 8, 9, 16, 48, 45, tzinfo=tzutc())

    >>> headers = "Last-Modified:  Mon, 09 Aug 2010 16:48:\\r\\n\\r\\n"
    >>> print get_time_header(
    ...     rfc822.Message(StringIO(headers)), 'last-modified', log)
    None

    >>> print get_time_header(rfc822.Message(StringIO(headers)), 'unknown', log)
    None

    """
    val = msg.get(name)
    if not val:
        return default

    try:
        return parse(val)
    except ValueError:
        if logger:
            logger.warning("Failed to parse date value '%s'", val)
        return default


def calc_age(age_value, date_value, request_time, response_time, now):
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

    apparent_age = max(timedeltazero, response_time - date_value)
    corrected_received_age = max(apparent_age, age_value)
    response_delay = response_time - request_time
    corrected_initial_age = corrected_received_age + response_delay
    resident_time = now - response_time
    current_age = corrected_initial_age + resident_time
    return current_age


def iter_header_values(header_val):
    """ Given the value of a header, return a generator which cracks all the
    lower-case values

    >>> list(iter_header_values(''))
    []
    >>> list(iter_header_values('test1, test3 , tesT2, Test4'))
    ['test1', 'test3', 'test2', 'test4']
    """
    if not header_val:
        return
    for bit in header_val.split(","):
        yield bit.strip().lower()


def iter_name_value_pairs(header_val):
    """ Given the value of a Cache-Control (or similar) header, return a
    generator which cracks all the vlaues - lower-case keys and anything
    after the '=' as a value (or None if no =)

    >>> list(iter_name_value_pairs(''))
    []
    >>> list(iter_name_value_pairs('test1=test1_1 , test3 , tesT2 = test2_1, Test4='))
    [('test1', 'test1_1'), ('test3', None), ('test2 ', ' test2_1'), ('test4', '')]
    """
    if not header_val:
        return
    for bit in iter_header_values(header_val):
        if '=' in bit:
            v, val = bit.split("=", 1)
        else:
            v = bit
            val = None
        yield v, val


# Optional length (hrmph - where did this come from?  RRC2616 doesn't seem to
# mention it, our tests don't hit it, and the impl was wrong (we previously
# checked for a content-length in the *client* request!)
re_ims_value = re.compile("([^;]+)((; *length=([0-9]+)$)|$)")

def get_if_modified_since(msg, logger=None):
    """ Parse an 'If-Modified-Since: date[;length=nnn]' header.  Return the
    raw date so we can string compare without parsing as an optimization.
    See above though - where does the length=xxx thing come from???

    >>> import rfc822, logging
    >>> from StringIO import StringIO

    >>> headers = ("Transfer-Encoding: some value\\r\\n"
    ...            "Connection: close\\r\\n"
    ...            "Cache-Control: max-age=10\\r\\n\\r\\n")
    >>> get_if_modified_since(rfc822.Message(StringIO(headers)))
    (None, None)

    >>> headers = "IF-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT;bbb\\r\\n\\r\\n"
    >>> get_if_modified_since(
    ...     rfc822.Message(StringIO(headers)), logging.getLogger())
    (None, None)

    >>> headers = "IF-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT\\r\\n\\r\\n"
    >>> get_if_modified_since(rfc822.Message(StringIO(headers)))
    ('Mon, 09 Aug 2010 16:48:45 GMT', None)

    >>> headers = "IF-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT; length=kjk\\r\\n\\r\\n"
    >>> get_if_modified_since(rfc822.Message(StringIO(headers)))
    (None, None)

    >>> headers = "IF-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT; length=348\\r\\n\\r\\n"
    >>> get_if_modified_since(rfc822.Message(StringIO(headers)))
    ('Mon, 09 Aug 2010 16:48:45 GMT', 348)

    """
    val = msg.get("If-Modified-Since")
    if not val:
        return None, None

    m = re_ims_value.match(val)
    if not m:
        if logger:
            logger.exception("Failed to parse 'If-Modified-Since: %s'", val)
        return None, None

    date = m.group(1)
    size = m.group(4)
    if size is not None:
        size = int(size)

    return date, size


def cleanup_hop_headers(response):
    """ RFC2616 13.5.1 defines "hop-by-hop" headers, which are ones
    we should remove, but note that Cookies and auth headers are
    *not* in this list (but itappears to allow the response itself
    to nominate other hop-by-hop headers in the 'Connection' header.
    Also, cache-control: no-cache=foo can be treated in exactly the same
    way, as both have the nett result of removing the header from the cache

    >>> import rfc822
    >>> from StringIO import StringIO
    >>> class FakeResponse:
    ...     def __init__(self, msg, status=200, reason="OK", length=None):
    ...         self.msg = msg
    ...         self.length = length
    ...         self.status = status
    ...         self.reason = reason

    # Transfer-Encoding is a "hop-by-hop" header.
    >>> headers = ("Transfer-Encoding: some value\\r\\n"
    ...            "Connection: close\\r\\n"
    ...            "Cache-Control: max-age=10\\r\\n\\r\\n")

    >>> resp = FakeResponse(rfc822.Message(StringIO(headers)))
    >>> cleanup_hop_headers(resp)
    ['200 OK', 'cache-control: max-age=10']

    >>> headers = ("X-Custom: some value\\r\\n"
    ...            "Connection: X-Custom\\r\\n"
    ...            "Cache-Control: max-age=10\\r\\n\\r\\n")

    >>> print cleanup_hop_headers(FakeResponse(rfc822.Message(StringIO(headers))))
    ['200 OK', 'cache-control: max-age=10']


    >>> headers = ("X-Custom: some value\\r\\n"
    ...            "Cache-Control: max-age=10,no-cache=x-custom\\r\\n\\r\\n")

    >>> print cleanup_hop_headers(FakeResponse(rfc822.Message(StringIO(headers))))
    ['200 OK', 'cache-control: max-age=10,no-cache=x-custom']

    """
    exclude_headers = set(hop_by_hop_headers)
    msg = response.msg
    conn = msg.get('connection')

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
                exclude_headers.add(v.lower())
                cc_exclude_seen = True

    # Nod to zope - no cache-control:no-cache header, we default to set-cookie
    if not cc_exclude_seen:
        exclude_headers.add('set-cookie')

    bits = ['%s %s' % (response.status, response.reason)]
    for h in iter(msg): # no iteritems :()
        if h.lower() not in exclude_headers:
            bits.append("%s: %s" % (h, msg[h]))

    return bits
