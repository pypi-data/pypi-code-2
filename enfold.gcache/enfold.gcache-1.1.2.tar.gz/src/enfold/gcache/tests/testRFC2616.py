# Test the cache semantics described in RFC2616.

import unittest
import rfc822
import sys, os, shutil, tempfile, time, logging
from cStringIO import StringIO
import datetime
from datetime import timedelta

logger = logging.getLogger()
hdlr = logging.FileHandler('test.log')
fmt = logging.Formatter(logging.BASIC_FORMAT)
hdlr.setFormatter(fmt)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

#sys.path.insert(0, os.path.abspath('../..'))
from enfold.gcache import cache, httpcache


class FakeConnection:

    def __init__(self, validation_responses):
        self.validation_responses = validation_responses
        self.headers = {}

    # Looks like a httplib.HTTPConnection() object.
    def putrequest(self, req, url):
        pass

    def putheader(self, header, value):
        vals = self.headers.setdefault(header.lower(), [])
        vals.append(value)

    def endheaders(self):
        pass

    def getresponse(self):
        resp, validator = self.validation_responses.pop(0)
        if validator:
            validator(self)
        return resp

    def close(self):
        pass


class CacheProvider(httpcache.CacheProvider):

    def __init__(self, validation_responses, logger = None):
        httpcache.CacheProvider.__init__(self, logger)
        self.validation_responses = validation_responses

    def open_host(self, scheme, host, port=None):
        assert scheme == 'http'
        return FakeConnection(self.validation_responses)


def FormatDate(d):
    return d.strftime("%a, %d %b %Y %H:%M:%S GMT")


class FakeResponse:

    def __init__(self, msg, status=200, reason="OK", length=None):
        self.msg = msg
        if length is not None:
            assert 'Content-Length' not in msg
            self.msg["Content-Length"] = str(length)
        self.status = status
        self.reason = reason

    def close(self):
        pass


def getHeaders(data):
    data_f = StringIO(data)
    return rfc822.Message(data_f)


class TestRFC2616(unittest.TestCase):

    def setUp(self):
        dirname = os.path.join(tempfile.gettempdir(), ".HTTPCache_TestCache")
        for i in range(3):
            if not os.path.isdir(dirname):
                break
            try:
                shutil.rmtree(dirname)
            except EnvironmentError:
                time.sleep(1)
        else:
            raise AssertionError("Failed to remove %r" % (dirname,))
        os.makedirs(dirname)
        self.cache_dir = dirname
        self.provider_validation_responses = []

        self.cache = cache.Cache(
            storage = httpcache.Storage(dirname),
            provider = CacheProvider(self.provider_validation_responses),
            max_size = 50000,
            default_age = 0)

    def ensureTimesNearlyEqual(self, t1, t2):
        # all tests use time granularity of > 1 sec
        self.failUnless(abs(t1-t2) < datetime.timedelta(seconds=1), (t1, t2, abs(t1-t2)))

    def tearDown(self):
        self.failIf(self.provider_validation_responses, "Validation responses were not consumed")
        self.cache._check()
        self.cache.close()
        shutil.rmtree(self.cache_dir)

    def getCachedHeaders(self, resp, meta):
        # see how the cache filters headers.
        meta, prefix = httpcache.get_response_meta_and_prefix(resp,
                                                              self.cache.now(),
                                                              self.cache.logger)
        f = StringIO('\r\n'.join(prefix))
        status = f.readline()
        self.failUnlessEqual(status, "200 OK\r\n")
        cached_msg = rfc822.Message(f)
        return cached_msg

    def setCacheResponseRaw(self, key, headers, data, status="200 OK"):
        now = self.cache.now()
        msg = rfc822.Message(StringIO(headers))
        assert 'content-length' not in msg, msg
        msg['content-length'] = str(len(data))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        full_data = status + '\r\n' + data
        meta.size = len(full_data)
        self.cache.set(key, (meta, full_data))


# RFC sections
# [Note that commentary related to EP is in square brackes.  Most other
#  text is direct quotes from the RFC]
# Section 9: ???
# 9.4: head

# Section 13: Caching in HTTP
# 13.5 Constructing Responses From Caches
# 13.5.1 End-to-end and Hop-by-hop Headers

class TestCaching(TestRFC2616):

    def testEndToEnd(self):
        headers = "X-Custom: some value\r\n" \
                  "Cache-Control: max-age=10\r\n" \
                  "\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        now = self.cache.now()
        meta = httpcache.httpmetadata(resp, now, now)
        # check the header makes it through the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failUnless('X-Custom' in cached_headers)

    def testHopByHop(self):
        # Transfer-Encoding is a "hop-by-hop" header.
        headers = "Transfer-Encoding: some value\r\n" \
                  "Cache-Control: max-age=10\r\n" \
                  "\r\n"
        now = self.cache.now()
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        meta = httpcache.httpmetadata(resp, now, now)
        # check the header makes it through the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('Transfer-Encoding' in cached_headers)

    def testHopByHopCustom(self):
        headers = "X-Custom: some value\r\n" \
                  "Connection: X-Custom\r\n" \
                  "Cache-Control: max-age=10\r\n" \
                  "\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        now = self.cache.now()
        meta = httpcache.httpmetadata(resp, now, now)
        # check the header did not make it through the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('X-Custom' in cached_headers)


class TestCachingNon200(TestRFC2616):

    def testDefaultUncachable(self):
        headers = "\r\n\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)), status=403,
                            reason="whatever")
        now = self.cache.now()
        self.assertRaises(cache.Uncachable,
                          httpcache.get_response_meta_and_prefix, resp, now, self.cache.logger)

    def testExplicitlyCachable(self):
        headers = "cache-control: max-age=10\r\n\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)), status=403,
                            reason="whateva")
        now = self.cache.now()
        meta, bits = httpcache.get_response_meta_and_prefix(resp, now, self.cache.logger)
        self.failUnlessEqual(bits[0], "403 whateva")
        self.failUnlessEqual(bits[1], "cache-control: max-age=10")

    def testExplicitlyCachableNotValidated(self):
        headers = "cache-control: max-age=1\r\netag: foo\r\n\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)), status=403,
                            reason="whateva")
        now = self.cache.now()
        meta, bits = httpcache.get_response_meta_and_prefix(resp, now, self.cache.logger)
        data = ''.join(bits)
        self.failUnlessRaises(KeyError, self.cache.provider.do_validate, 'httpxxx', 'whateva', '/whatever', meta, data)


# 13.5.2 Non-modifiable Headers
# [Most of this should work in EP]

# 13.5.3 Combining Headers

# The end-to-end headers stored in the cache entry are used for the
# constructed response, except that:
# * any stored Warning headers with warn-code 1xx (see section
#   14.46) MUST be deleted from the cache entry and the forwarded response.
# * any stored Warning headers with warn-code 2xx MUST be retained in the
#   cache entry and the forwarded response.
# * any end-to-end headers provided in the 304 or 206 response MUST replace
#   the corresponding headers from the cache entry.
# The following HTTP/1.1 headers are hop-by-hop headers:
#  - Connection, - Keep-Alive, - Proxy-Authenticate, - Proxy-Authorization
#  - TE, - Trailers, - Transfer-Encoding, - Upgrade
# All other headers defined by HTTP/1.1 are end-to-end headers.
# Other hop-by-hop headers MUST be listed in a Connection header,
# [NOTE: EP does not support any of the above]

# Section 14: Header Field Definitions
# 14.6 Age:
class TestAge(TestRFC2616):

    def testSimple(self):
        now = self.cache.now()
        headers = "Date: %s\r\n" \
                  % (FormatDate(now))
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta = httpcache.httpmetadata(FakeResponse(msg, length=3), now, now)
        self.cache.set('test_url', (meta, 'foo'))
        time.sleep(1)
        # Now ask it to patch up some headers with new info - it should have
        # a 1 second age.
        self.failIf("age" in msg, "should not have an age yet")
        meta.fixup_response_headers(msg)
        self.failUnless(msg.get("age") in ["1", "2"], msg.get("age"))
        time.sleep(1)
        meta.fixup_response_headers(msg)
        # time skew :(
        self.failUnless(msg.get("age") in ["2", "3", "4"], msg.get("age"))

    def testSimpleBadDate(self):
        # A bad date should just be treated like no date.
        now = self.cache.now()
        headers = "Date: bad_date\r\n" \
                  "\r\n"
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta = httpcache.httpmetadata(FakeResponse(msg, length=3), now, now)
        self.cache.set('test_url', (meta, 'foo'))
        time.sleep(1)
        # Now ask it to patch up some headers with new info - it should have
        # a 1 second age.
        self.failIf("age" in msg, "should not have an age yet")
        meta.fixup_response_headers(msg)
        self.failUnlessEqual(msg.get("age"), "1")


# 14.8 Authorization
# """When a shared cache (see section 13.7) receives a request
#    containing an Authorization field, it MUST NOT return the
#    corresponding response as a reply to any other request, unless one
#    of the following specific exceptions holds:
#    ..."""
class TestAuthorization(TestRFC2616):
    def testAuthorizationPreventsStoring(self):
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=3\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        # RFC says we MUST NOT return it, even if it has "normal" headers
        # that would allow it to be cached.  It doesn't mention we can
        # use it after validation it, so EP doesn't keep it.
        self.assertRaises(cache.Uncachable,
                          httpcache.httpmetadata, FakeResponse(msg), now)

    def testCustomAuthorizationPreventsStoring(self):
        # we provide a mechanism to allow overriding of "if_authorized" -
        # check that works.
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "X-Custom: foo\r\n" \
                  "Cache-Control: max-age=3\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        # RFC says we MUST NOT return it, even if it has "normal" headers
        # that would allow it to be cached.  It doesn't mention we can
        # use it after validation it, so EP doesn't keep it.
        resp = FakeResponse(msg)
        resp.is_authorized = lambda: True
        self.assertRaises(cache.Uncachable,
                          httpcache.httpmetadata, resp, now)

    def testAuthorizationExplicitlyPublic(self):
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=3, public\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # should be stale in the future!
        self.failUnless(meta.t_stale > now, (meta.t_stale, now))

    def testAuthorizationExplicitlySMaxAge(self):
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=10, s-maxage=5\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # s-maxage trumps max-age, and is enough to consider it fresh
        expect_stale = now+datetime.timedelta(seconds=5)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    def testAuthorizationExplicitlyMustRevalidate(self):
        # a must-revalidate header is enough for it to be considered fresh.
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=10, must-revalidate\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # must revalidate means our max-age is honoured
        expect_stale = now+datetime.timedelta(seconds=10)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)


# 14.9 Cache-Control
# Test headers in the *response* from the server we are caching
class TestCacheControlResponse(TestRFC2616):

    def testPrivate(self):
        """Test cache-control: private"""
        headers = "Last-Modified: %s\r\n" \
                  % (FormatDate(self.cache.now()),)
        msg = rfc822.Message(StringIO(headers))
        now = self.cache.now()
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # Now try it with a cache-control header set to 'private'.
        headers = "Date-Modified: %s\r\n" \
                  "Cache-Control: max-age=3600, s-maxage=3600, private\r\n\r\n" \
                  % (FormatDate(self.cache.now()),)
        msg = rfc822.Message(StringIO(headers))
        self.assertRaises(
            cache.Uncachable,
            httpcache.httpmetadata, FakeResponse(msg), self.cache.now())

    def testNoStore(self):
        """Test cache-control: no-store"""
        headers = "Date-Modified: %s\r\n" \
                  "Cache-Control: no-store\r\n\r\n" \
                  % (FormatDate(self.cache.now()),)
        msg = rfc822.Message(StringIO(headers))
        self.assertRaises(cache.Uncachable,
                          httpcache.httpmetadata, FakeResponse(msg), self.cache.now())

    #s-maxage
    #   If a response includes an s-maxage directive, then for a shared cache
    #   (but not for a private cache), the maximum age specified by this
    #   directive overrides the maximum age specified by either the max-age
    #   directive or the Expires header. The s-maxage directive also implies the
    #   semantics of the proxy-revalidate directive (see section 14.9.4), i.e.,
    #   that the shared cache must not use the entry after it becomes stale to
    #   respond to a subsequent request without first revalidating it with the
    #   origin server. The s- maxage directive is always ignored by a private
    #   cache.
    def testSMaxAge(self):
        now = self.cache.now()
        # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
        headers = "Last-Modified: %s\r\n" \
                  "Cache-Control: s-maxage=3\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # s-maxage trumps expiry
        expect_stale = now+datetime.timedelta(seconds=3)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

        # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
        headers = "Last-Modified: %s\r\n" \
                  "Cache-Control: s-maxage=3, proxy-revalidate\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # s-maxage trumps expiry
        expect_stale = now+datetime.timedelta(seconds=3)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    # max-age: similar to s-maxage
    def testMaxAge(self):
        now = self.cache.now()
        # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
        headers = "Last-Modified: %s\r\n" \
                  "Cache-Control: max-age=3\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        # max-age trumps expiry
        expect_stale = now+datetime.timedelta(seconds=3)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    def testMaxAndSMaxAge(self):
        now = self.cache.now()
        # Check with both headers in both orders.
        for cc in "max-age=3, s-maxage=4", "s-maxage=4, max-age=3":
            # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
            headers = "Last-Modified: %s\r\n" \
                      "Cache-Control: %s\r\n" \
                      "Expires: %s\r\n\r\n" \
                      % (FormatDate(now),cc,now+datetime.timedelta(seconds=5))
            msg = rfc822.Message(StringIO(headers))
            meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
            # s-maxage trumps max-age and expiry
            expect_stale = now+datetime.timedelta(seconds=4)
            self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    def testUpdatedMaxAge(self):
        # Set a max-age of 0, and have the validation response set a different
        # max-age
        now = self.cache.now()
        # VALIDATION headers - expires in the future.
        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-age=1'
        self.provider_validation_responses.append(
            (FakeResponse(msg, 304, "Not Modified"), None)
        )

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-age=0'
        msg['Last-Modified'] = FormatDate(now)

        meta = httpcache.httpmetadata(FakeResponse(msg, length=9), now, now)
        data = '200 OK\r\nblah blah'
        meta.size = len(data)
        self.cache.set('test_url', (meta, data))
        # This should trigger a validation, and the new maxage seen
        self.cache.get('test_url')
        self.failIf(self.provider_validation_responses, "Validation response was not consumed")
        # Been validated, should now expire in the future, so no validation
        self.cache.get('test_url')
        # queue the validation response for the next validation - no
        # cache-control header, so the most-recent (max-age=1) should be used.
        msg = rfc822.Message(StringIO())
        self.provider_validation_responses.append(
            (FakeResponse(msg, 304, "Not Modified"), None)
        )
        # sleep for the 1 second.
        time.sleep(1.1)
        # re-fetch - should validate.
        self.cache.get('test_url')
        self.failIf(self.provider_validation_responses, "Validation response was not consumed")
        # re-fetch - 1 sec should still be in force, so no validation.
        self.cache.get('test_url')

    def testPragmaNoCache(self):
        now = self.cache.now()
        # Expires in 5 seconds, but pragma: no-cache says stale now.
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "Pragma: no-cache\r\n" \
                  % (FormatDate(now),
                     FormatDate(now+datetime.timedelta(seconds=5)))
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        self.ensureTimesNearlyEqual(meta.t_stale, now)

    def testCCNoCache(self):
        # Test a 'cache-control: no-cache' (ie, without field names specified)
        now = self.cache.now()
        # Expires in 5 seconds, but cache-control: no-cache says stale now.
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "Cache-Control: no-cache\r\n" \
                  % (FormatDate(now),
                     FormatDate(now+datetime.timedelta(seconds=5)))
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg), now, now)
        self.ensureTimesNearlyEqual(meta.t_stale, now)

    def testCCNoCacheField(self):
        # Test a 'cache-control: no-cache=header' instruction.
        now = self.cache.now()
        expires = now+datetime.timedelta(seconds=5)
        # Expires in 5 seconds, but cache-control: no-cache says stale now.
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "X-Private: topsecret\r\n" \
                  "Set-Cookie: cookie\r\n" \
                  "Cache-Control: no-cache=X-Private\r\n" \
                  % (FormatDate(now),
                     FormatDate(expires))
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        meta = httpcache.httpmetadata(resp, now, now)
        # no-cache with a header only applies to the header, not the response
        # itself - so it should expire as per the response.
        self.ensureTimesNearlyEqual(meta.t_stale, expires)
        # and check we don't get that header from the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('X-Private' in cached_headers)
        # but set-cookie *should* be in the cache - we trust the server
        # knows what it is doing if it specified a field.
        self.failUnless('Set-Cookie' in cached_headers)

    def testCCNoCacheFieldDefault(self):
        # Test a 'cache-control: no-cache' instruction implies
        # no-cache=set-cookie was specified.
        now = self.cache.now()
        expires = now+datetime.timedelta(seconds=5)
        # Expires in 5 seconds, but cache-control: no-cache says stale now.
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "Set-Cookie: topsecret\r\n" \
                  "X-Custom: custom\r\n" \
                  "Cache-Control: no-cache\r\n" \
                  % (FormatDate(now),
                     FormatDate(expires))
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        meta = httpcache.httpmetadata(resp, now, now)
        # check we don't get that header from the cache
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('Set-Cookie' in cached_headers)
        # and check we did get the custom header not specified.
        self.failUnless('X-Custom' in cached_headers)


# Test cache-control headers in the client request
class TestCacheControlRequest(TestRFC2616):

    def _addCachedItem(self, key='test_url', expires=5):
        now = self.cache.now()
        # wipe msecs for sake of testing
        now = datetime.datetime(now.year, now.month, now.day, now.hour,
                                now.minute, now.second, 0, now.tzinfo)
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=expires))
        msg = rfc822.Message(StringIO(headers))
        meta = httpcache.httpmetadata(FakeResponse(msg, length=3), now, now)
        self.cache.set(key, (meta, 'foo'))
        return now

    def testMaxAge(self):
        now = self._addCachedItem()
        meta, data = self.cache['test_url']
        cached_headers = getHeaders(data)

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-age=2'

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=1),
                            cached_headers, msg))
        self.failIf(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=3),
                            cached_headers, msg))

    def testMinFresh(self):
        now = self._addCachedItem()
        meta, data = self.cache['test_url']
        cached_headers = getHeaders(data)

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'min-fresh=3'

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=1),
                            cached_headers, msg))
        self.failIf(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=3),
                            cached_headers, msg))

    def testMaxStale(self):
        now = self._addCachedItem()
        meta, data = self.cache['test_url']
        cached_headers = getHeaders(data)

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-stale=5'

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=1),
                            cached_headers, msg))

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=10),
                            cached_headers, msg))

        self.failIf(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=11),
                            cached_headers, msg))

# 14.10 Connection
# The Connection general-header field ... MUST NOT be communicated by proxies over further connections.
# HTTP/1.1 proxies MUST parse the Connection header field before a message is
# forwarded and, for each connection-token in this field, remove any header
# field(s) from the message with the same name as the connection-token.


# Need to test:
# 14.16 Content-Range
# [EP does not support this]
# 14.18 Date
# [cached response should have original date but updated Age header: EP
# does not do this for cached responses]
# 14.19 ETag
# 14.20 Expect (maybe just EP?)
# 14.21 Expires
class TestExpires(TestRFC2616):

    def testPast(self):
        """Test expires: in the past"""
        # We expect that the item will be considered stale (expiry in the
        # past), and as the validation indicated the existing (invalid)
        # metadata is OK, it can be fetched.
        # Prime a validation response.
        self.provider_validation_responses.append(
            (FakeResponse(
                    rfc822.Message(StringIO("\r\n\r\n")),304,"Not Modified"), None)
            )

        now = self.cache.now()
        mod = now - datetime.timedelta(days=365)
        expires = mod + datetime.timedelta(days=1)
        headers = "Date: %s\r\n" \
                  "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  % (FormatDate(mod), FormatDate(mod), FormatDate(expires))
        self.setCacheResponseRaw('test_url', headers, 'data')
        # This should trigger a validation
        self.cache.get('test_url')

    def testNotModified(self):
        """Test expires: expires in the past and Last-modified > expires"""
        # i think we should get Uncacheble exception
        now = self.cache.now()
        expires = now - datetime.timedelta(days=365)
        headers = "Date: %s\r\n" \
                  "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  % (FormatDate(now), FormatDate(now), FormatDate(expires))

        msg = rfc822.Message(StringIO(headers))
        self.assertRaises(cache.Uncachable,
                          httpcache.httpmetadata, FakeResponse(msg), now, now)

        # but only if server does not provide Cache-Control header
        headers = headers + "Cache-Control: max-age=3600\r\n"
        msg = rfc822.Message(StringIO(headers))
        httpcache.httpmetadata(FakeResponse(msg), now, now)

    def testUpdatedExpires(self):
        """Test that a new expires in a validation response is used"""
        now = self.cache.now()
        future_expires = now + datetime.timedelta(days=365)
        past_expires = now - datetime.timedelta(days=365)
        # VALIDATION headers - expires in the future.
        headers = "Expires: %s\r\n\r\n" % FormatDate(future_expires)
        msg = rfc822.Message(StringIO(headers))
        self.provider_validation_responses.append(
            (FakeResponse(msg, 304, "Not Modified"), None)
        )

        headers = "Expires: %s\r\n" \
                  "Last-Modified: %s\r\n" \
                  "\r\n" % (FormatDate(past_expires), FormatDate(past_expires))
        self.setCacheResponseRaw('test_url', headers, 'data')
        # This should trigger a validation, and the new expiry time seen
        self.cache.get('test_url')
        # Been validated, should now expire in the future, so no validation
        self.cache.get('test_url')


# 14.24 If-Match
# 14.25 If-Modified-Since
# 14.26 If-None-Match
# 14.27 If-Range
# 14.28 If-Unmodified-Since
# [NOTE: We currently only support a subset of the above]
# 14.29 Last-Modified
# 14.32 Pragma
# 14.35 Range
# 14.44 Vary
class TestVary(TestRFC2616):

    def testSimple(self):
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "X-Foo: foo\r\n" \
                  "Vary: X-Foo\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta = httpcache.httpmetadata(FakeResponse(msg, length=3), now, now)
        self.cache.set('test_url', (meta, 'foo'))
        # check we can read it with the correct header
        client_headers = "X-Foo: foo\n\n"
        client_msg = rfc822.Message(StringIO(client_headers+'\r\n'))
        meta = self.cache.getmeta('test_url')

        self.failUnless(
            meta.fresh_for_request(now, msg, client_msg))
        # with a bad value.
        client_headers = "X-Foo: bar\n\n"
        client_msg = rfc822.Message(StringIO(client_headers+'\r\n'))
        meta = self.cache.getmeta('test_url')
        self.failIf(
            meta.fresh_for_request(now, msg, client_msg))

    def testOurMeta(self):
        # Test using get_response_meta_and_prefix
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "X-Foo: foo\r\n" \
                  "Vary: X-Foo\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta, prefix = httpcache.get_response_meta_and_prefix(
            FakeResponse(msg, length=3), now, self.cache.logger)
        f = StringIO('\r\n'.join(prefix))
        status = f.readline()
        self.failUnlessEqual(status, "200 OK\r\n")
        cache_msg = rfc822.Message(f)
        self.cache.set('test_url', (meta, 'foo'))
        # check we can read it with the correct header
        client_headers = "X-Foo: foo\n\n"
        client_msg = rfc822.Message(StringIO(client_headers+'\r\n'))
        meta = self.cache.getmeta('test_url')

        self.failUnless(
            meta.fresh_for_request(now, cache_msg, client_msg))
        # with a bad value.
        client_headers = "X-Foo: bar\n\n"
        client_msg = rfc822.Message(StringIO(client_headers+'\r\n'))
        meta = self.cache.getmeta('test_url')
        self.failIf(
            meta.fresh_for_request(now, cache_msg, client_msg))

    def testVaryRequestHeaders(self):
        # Test using get_response_meta_and_prefix
        # XXX - this test currently fails, as our cache does not store
        # all headers, just a select few - and this test uses 'Vary' on
        # a header that is *not* stored.
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "X-Foo: foo\r\n" \
                  "Vary: X-Foo\r\n\r\n" \
                  % (FormatDate(now),now)
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta, prefix = httpcache.get_response_meta_and_prefix(
            FakeResponse(msg, length=3), now, self.cache.logger)
        f = StringIO('\r\n'.join(prefix))
        status = f.readline()
        self.failUnlessEqual(status, "200 OK\r\n")
        cache_msg = rfc822.Message(f)
        self.cache.set('test_url', (meta, 'foo'))

        # validation function for the validate request.  We expect to see the
        # clients headers - ones mentioned in Vary and those not.
        def validate(resp):
            self.failUnlessEqual(
                resp.headers.get("x-foo"), ["bar"], resp.headers)
            self.failUnlessEqual(
                resp.headers.get("something"), ["val1,val2"], resp.headers)

        # Queue up the validation response.
        self.provider_validation_responses.append(
            (FakeResponse(rfc822.Message(
                        StringIO("\r\n\r\n")), 304, "Not Modified"), validate))
        req_headers = "X-Foo: bar\r\n" \
                      "Something: val1\r\n" \
                      "Something: val2\r\n\r\n"
        req_msg = rfc822.Message(StringIO(req_headers))
        self.cache.validate_item(
            now, 'test_url', meta, '200 OK\r\ndata', None, (req_msg,))


class TestIfNoneMatchWithNonEtagCacheEntry(TestRFC2616):

    def testSimple(self):
        now = self.cache.now()
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "Cache-Control: max-age=0, s-maxage=300, proxy-revalidate"\
                  % (FormatDate(now),now+timedelta(seconds=100))
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta, prefix = httpcache.get_response_meta_and_prefix(
            FakeResponse(msg, length=3), now, self.cache.logger)
        cache_msg = rfc822.Message(StringIO('\r\n'.join(prefix)))
        self.cache.set('test_url', (meta, 'foo'))

        # check same cache entry with If-None-Match
        client_headers = "If-None-Match: test-etag-value\r\n"
        client_msg = rfc822.Message(StringIO(client_headers))

        self.failIf(meta.fresh_for_request(now, cache_msg, client_msg))


# 14.45 Via

def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    return suite
