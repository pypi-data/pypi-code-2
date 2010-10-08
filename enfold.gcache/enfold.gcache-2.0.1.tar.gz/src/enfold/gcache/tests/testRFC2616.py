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

from enfold.gcache import cache, httpcache, utils
from enfold.gcache.interfaces import Uncachable


class FakeConnection:

    def __init__(self, responses):
        self.responses = responses
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
        resp, validator = self.responses.pop(0)
        if validator:
            validator(self)
        return resp

    def close(self):
        pass


class CacheProvider(httpcache.CacheProvider):

    def __init__(self, responses, logger = None):
        super(CacheProvider, self).__init__('http', '', logger)
        self.responses = responses

    def open_host(self, scheme, host, port=None):
        return FakeConnection(self.responses)


def FormatDate(d):
    return d.strftime("%a, %d %b %Y %H:%M:%S GMT")


def getHeaders(data):
    data_f = StringIO(data)
    return rfc822.Message(data_f)


class FakeResponse:

    def __init__(self, msg, status=200, reason="OK", length=None, data=None):
        self.msg = msg
        if length is not None:
            assert 'Content-Length' not in msg
            self.msg["Content-Length"] = str(length)
        self.length = length
        self.status = status
        self.reason = reason
        self.data = data

    def close(self):
        pass

    def read(self):
        if self.data:
            return self.data
        return ''.join([' ' for i in range(self.length or 0)])


class TestRFC2616(unittest.TestCase):

    metadata = httpcache.httpmetadata
    storageClass = httpcache.Storage

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
        self.provider_responses = []

        self.cache = cache.Cache(
            storage = self.storageClass(dirname, logger),
            provider = CacheProvider(self.provider_responses, logger),
            max_size = 50000,
            default_age = 0)

    def ensureTimesNearlyEqual(self, t1, t2):
        # all tests use time granularity of > 1 sec
        self.failUnless(abs(t1-t2) < datetime.timedelta(seconds=1),
                        (t1, t2, abs(t1-t2)))

    def tearDown(self):
        self.failIf(self.provider_responses,
                    "Validation responses were not consumed")
        try:
            self.cache._check()
        except:
            import traceback
            traceback.print_stack()
            raise
        self.cache.close()
        shutil.rmtree(self.cache_dir)

    def getCachedHeaders(self, resp, meta):
        # see how the cache filters headers.
        now = utils.now()
        prefix = utils.cleanup_hop_headers(resp)
        meta = self.metadata(resp, now, now, logger)

        f = StringIO('\r\n'.join(prefix))
        status = f.readline()
        self.failUnlessEqual(status, "200 OK\r\n")
        cached_msg = rfc822.Message(f)
        return cached_msg

    def setCacheResponseRaw(self, key, headers, data, status="200 OK"):
        now = utils.now()
        msg = rfc822.Message(StringIO(headers))
        assert 'content-length' not in msg, msg
        msg['content-length'] = str(len(data))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
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
        now = utils.now()
        meta = self.metadata(resp, now, now, logger)
        # check the header makes it through the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failUnless('X-Custom' in cached_headers)

    def testHopByHop(self):
        # Transfer-Encoding is a "hop-by-hop" header.
        headers = "Transfer-Encoding: some value\r\n" \
                  "Cache-Control: max-age=10\r\n" \
                  "\r\n"
        now = utils.now()
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        meta = self.metadata(resp, now, now, logger)
        # check the header makes it through the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('Transfer-Encoding' in cached_headers)

    def testHopByHopCustom(self):
        headers = "X-Custom: some value\r\n" \
                  "Connection: X-Custom\r\n" \
                  "Cache-Control: max-age=10\r\n" \
                  "\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)))
        now = utils.now()
        meta = self.metadata(resp, now, now, logger)
        # check the header did not make it through the cache.
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('X-Custom' in cached_headers)


class TestCachingNon200(TestRFC2616):

    def testDefaultUncachable(self):
        headers = "\r\n\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)), status=403,
                            reason="whatever")
        now = utils.now()
        self.assertRaises(Uncachable, self.metadata, resp, now, now, logger)

    def testExplicitlyCachable(self):
        headers = "cache-control: max-age=10\r\n\r\n"
        resp = FakeResponse(
            rfc822.Message(StringIO(headers)), status=403, reason="whateva")

        now = utils.now()
        bits = utils.cleanup_hop_headers(resp)
        meta = self.metadata(resp, now, now, logger)

        self.failUnlessEqual(bits[0], "403 whateva")
        self.failUnlessEqual(bits[1], "cache-control: max-age=10")

    def testExplicitlyCachableNotValidated(self):
        headers = "cache-control: max-age=1\r\netag: foo\r\n\r\n"
        resp = FakeResponse(rfc822.Message(StringIO(headers)), status=403,
                            reason="whateva")

        now = utils.now()
        bits = utils.cleanup_hop_headers(resp)
        meta = self.metadata(resp, now, now, logger)

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
        now = utils.now()
        headers = "Date: %s\r\n" \
                  % (FormatDate(now))
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta = self.metadata(FakeResponse(msg, length=3), now, now, logger)
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
        now = utils.now()
        headers = "Date: bad_date\r\n" \
                  "\r\n"
        msg = rfc822.Message(StringIO(headers+'\r\n'))
        meta = self.metadata(
            FakeResponse(msg, length=3), now, now, logger)
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
        now = utils.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=3\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        # RFC says we MUST NOT return it, even if it has "normal" headers
        # that would allow it to be cached.  It doesn't mention we can
        # use it after validation it, so EP doesn't keep it.
        self.assertRaises(
            cache.Uncachable,
            self.metadata, FakeResponse(msg), now, now, logger)

    def testCustomAuthorizationPreventsStoring(self):
        # we provide a mechanism to allow overriding of "if_authorized" -
        # check that works.
        now = utils.now()
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
                          self.metadata, resp, now, now, logger)

    def testAuthorizationExplicitlyPublic(self):
        now = utils.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=3, public\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # should be stale in the future!
        self.failUnless(meta.t_stale > now, (meta.t_stale, now))

    def testAuthorizationExplicitlySMaxAge(self):
        now = utils.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=10, s-maxage=5\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # s-maxage trumps max-age, and is enough to consider it fresh
        expect_stale = now+datetime.timedelta(seconds=5)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    def testAuthorizationExplicitlyMustRevalidate(self):
        # a must-revalidate header is enough for it to be considered fresh.
        now = utils.now()
        headers = "Last-Modified: %s\r\n" \
                  "Authorization: topsecret\r\n" \
                  "Cache-Control: max-age=10, must-revalidate\r\n" \
                  "\r\n" % (FormatDate(now),)
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # must revalidate means our max-age is honoured
        expect_stale = now+datetime.timedelta(seconds=10)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)


# 14.9 Cache-Control
# Test headers in the *response* from the server we are caching
class TestCacheControlResponse(TestRFC2616):

    def testPrivate(self):
        """Test cache-control: private"""
        headers = "Last-Modified: %s\r\n" \
                  % (FormatDate(utils.now()),)
        msg = rfc822.Message(StringIO(headers))
        now = utils.now()
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # Now try it with a cache-control header set to 'private'.
        headers = "Date-Modified: %s\r\n" \
                  "Cache-Control: max-age=3600, s-maxage=3600, private\r\n\r\n" \
                  % (FormatDate(utils.now()),)
        msg = rfc822.Message(StringIO(headers))
        self.assertRaises(
            cache.Uncachable,
            self.metadata, FakeResponse(msg),
            utils.now(), utils.now(), logger)

    def testNoStore(self):
        """Test cache-control: no-store"""
        headers = "Date-Modified: %s\r\n" \
                  "Cache-Control: no-store\r\n\r\n" \
                  % (FormatDate(utils.now()),)
        msg = rfc822.Message(StringIO(headers))
        self.assertRaises(
            cache.Uncachable,
            self.metadata, FakeResponse(msg),
            utils.now(), utils.now(), logger)

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
        now = utils.now()
        # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
        headers = "Last-Modified: %s\r\n" \
                  "Cache-Control: s-maxage=3\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # s-maxage trumps expiry
        expect_stale = now+datetime.timedelta(seconds=3)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

        # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
        headers = "Last-Modified: %s\r\n" \
                  "Cache-Control: s-maxage=3, proxy-revalidate\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # s-maxage trumps expiry
        expect_stale = now+datetime.timedelta(seconds=3)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    # max-age: similar to s-maxage
    def testMaxAge(self):
        now = utils.now()
        # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
        headers = "Last-Modified: %s\r\n" \
                  "Cache-Control: max-age=3\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=5))
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        # max-age trumps expiry
        expect_stale = now+datetime.timedelta(seconds=3)
        self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    def testMaxAndSMaxAge(self):
        now = utils.now()
        # Check with both headers in both orders.
        for cc in "max-age=3, s-maxage=4", "s-maxage=4, max-age=3":
            # Expires in 5 seconds, but cache-control: s-maxage says 3 secs
            headers = "Last-Modified: %s\r\n" \
                      "Cache-Control: %s\r\n" \
                      "Expires: %s\r\n\r\n" \
                      % (FormatDate(now),cc,now+datetime.timedelta(seconds=5))
            msg = rfc822.Message(StringIO(headers))
            meta = self.metadata(FakeResponse(msg), now, now, logger)
            # s-maxage trumps max-age and expiry
            expect_stale = now+datetime.timedelta(seconds=4)
            self.ensureTimesNearlyEqual(meta.t_stale, expect_stale)

    def testUpdatedMaxAge(self):
        # Set a max-age of 0, and have the validation response set a different
        # max-age
        now = utils.now()
        # VALIDATION headers - expires in the future.
        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-age=1'
        self.provider_responses.append(
            (FakeResponse(msg, 304, "Not Modified"), None))

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-age=0'
        msg['Last-Modified'] = FormatDate(now)

        ckey = CacheProvider.generate_key('test_url', {}, msg)

        meta = self.metadata(FakeResponse(msg, length=9), now, now, logger)
        data = '200 OK\r\nblah blah'
        meta.size = len(data)
        self.cache.set(ckey, (meta, data))

        # This should trigger a validation, and the new maxage seen
        self.cache.get(ckey)
        self.failIf(
            self.provider_responses,
            "Validation response was not consumed")

        # Been validated, should now expire in the future, so no validation
        self.cache.get(ckey)
        # queue the validation response for the next validation - no
        # cache-control header, so the most-recent (max-age=1) should be used.
        msg = rfc822.Message(StringIO())
        self.provider_responses.append(
            (FakeResponse(msg, 304, "Not Modified"), None))

        # sleep for the 1 second.
        time.sleep(1.1)

        # re-fetch - should validate.
        self.cache.get(ckey)
        self.failIf(
            self.provider_responses,
            "Validation response was not consumed")

        # re-fetch - 1 sec should still be in force, so no validation.
        self.cache.get(ckey)

    def testCCNoCache(self):
        # Test a 'cache-control: no-cache' (ie, without field names specified)
        now = utils.now()
        # Expires in 5 seconds, but cache-control: no-cache says stale now.
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  "Cache-Control: no-cache\r\n" \
                  % (FormatDate(now),
                     FormatDate(now+datetime.timedelta(seconds=5)))
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg), now, now, logger)
        self.ensureTimesNearlyEqual(meta.t_stale, now)

    def testCCNoCacheField(self):
        # Test a 'cache-control: no-cache=header' instruction.
        now = utils.now()
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
        meta = self.metadata(resp, now, now, logger)
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
        now = utils.now()
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
        meta = self.metadata(resp, now, now, logger)
        # check we don't get that header from the cache
        cached_headers = self.getCachedHeaders(resp, meta)
        self.failIf('Set-Cookie' in cached_headers)
        # and check we did get the custom header not specified.
        self.failUnless('X-Custom' in cached_headers)


# Test cache-control headers in the client request
class TestCacheControlRequest(TestRFC2616):

    def _addCachedItem(self, key='test_url', expires=5):
        now = utils.now()
        # wipe msecs for sake of testing
        now = datetime.datetime(now.year, now.month, now.day, now.hour,
                                now.minute, now.second, 0, now.tzinfo)
        headers = "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n\r\n" \
                  % (FormatDate(now),now+datetime.timedelta(seconds=expires))
        msg = rfc822.Message(StringIO(headers))
        meta = self.metadata(FakeResponse(msg, length=3), now, now, logger)
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
                            cached_headers, msg, logger))
        self.failIf(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=3),
                            cached_headers, msg, logger))

    def testMinFresh(self):
        now = self._addCachedItem()
        meta, data = self.cache['test_url']
        cached_headers = getHeaders(data)

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'min-fresh=3'

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=1),
                            cached_headers, msg, logger))
        self.failIf(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=3),
                            cached_headers, msg, logger))

    def testMaxStale(self):
        now = self._addCachedItem()
        meta, data = self.cache['test_url']
        cached_headers = getHeaders(data)

        msg = rfc822.Message(StringIO())
        msg['Cache-Control'] = 'max-stale=5'

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=1),
                            cached_headers, msg, logger))

        self.failUnless(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=10),
                            cached_headers, msg, logger))

        self.failIf(meta.fresh_for_request(
                            now+datetime.timedelta(seconds=11),
                            cached_headers, msg, logger))

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
        self.provider_responses.append(
            (FakeResponse(
                    rfc822.Message(StringIO("\r\n\r\n")),304,"Not Modified"), None)
            )

        now = utils.now()
        mod = now - datetime.timedelta(days=365)
        expires = mod + datetime.timedelta(days=1)
        headers = "Date: %s\r\n" \
                  "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  % (FormatDate(mod), FormatDate(mod), FormatDate(expires))
        key = self.cache.provider.generate_key(
            '/test_url', {}, rfc822.Message(StringIO(headers)))
        self.setCacheResponseRaw(key, headers, 'data')
        # This should trigger a validation
        self.cache.get(key)

    def testNotModified(self):
        """Test expires: expires in the past and Last-modified > expires"""
        # i think we should get Uncacheble exception
        now = utils.now()
        expires = now - datetime.timedelta(days=365)
        headers = "Date: %s\r\n" \
                  "Last-Modified: %s\r\n" \
                  "Expires: %s\r\n" \
                  % (FormatDate(now), FormatDate(now), FormatDate(expires))

        msg = rfc822.Message(StringIO(headers))
        self.assertRaises(
            Uncachable, self.metadata, FakeResponse(msg), now, now, logger)

        # but only if server does not provide Cache-Control header
        headers = headers + "Cache-Control: max-age=3600\r\n"
        msg = rfc822.Message(StringIO(headers))
        self.metadata(FakeResponse(msg), now, now, logger)

    def testUpdatedExpires(self):
        """Test that a new expires in a validation response is used"""
        now = utils.now()
        future_expires = now + datetime.timedelta(days=365)
        past_expires = now - datetime.timedelta(days=365)
        # VALIDATION headers - expires in the future.
        headers = "Expires: %s\r\n\r\n" % FormatDate(future_expires)
        msg = rfc822.Message(StringIO(headers))
        self.provider_responses.append(
            (FakeResponse(msg, 304, "Not Modified"), None))

        headers = "Expires: %s\r\n" \
                  "Last-Modified: %s\r\n" \
                  "\r\n" % (FormatDate(past_expires), FormatDate(past_expires))
        key = CacheProvider.generate_key('test_url', {}, msg)

        self.setCacheResponseRaw(key, headers, 'data')
        # This should trigger a validation, and the new expiry time seen
        self.cache.get(key)
        # Been validated, should now expire in the future, so no validation
        self.cache.get(key)


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    return suite
