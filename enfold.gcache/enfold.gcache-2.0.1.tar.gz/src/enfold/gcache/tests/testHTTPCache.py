# Test the cache semantics described in RFC2616.
"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import unittest
import time, datetime
from rfc822 import Message
from cStringIO import StringIO
from enfold.gcache import utils, httpcache
from enfold.gcache.interfaces import Uncachable

from testRFC2616 import CacheProvider
from testRFC2616 import logger, FormatDate, FakeResponse, TestRFC2616



class TestHTTPMetadata(TestRFC2616):

    def testUpdateFromResponse(self):
        now = utils.now()

        # use 0 if 'age' is broken and now if date is not supplied
        msg = Message(StringIO(
                "Cache-control: max-age=10\r\n"
                "Age: bad_age\r\n"))

        meta = self.metadata(FakeResponse(msg), now, now, logger)
        self.ensureTimesNearlyEqual(
            meta.t_stale, now+datetime.timedelta(seconds=10))

        # Uncachable because max-age or s-maxage are broken
        msg = Message(StringIO(
                "Cache-control: max-age=broken\r\n"))
        self.assertRaises(
            Uncachable, self.metadata, FakeResponse(msg), now, now, logger)

        msg = Message(StringIO(
                "Cache-control: s-maxage=broken\r\n"))
        self.assertRaises(
            Uncachable, self.metadata, FakeResponse(msg), now, now, logger)

        # fix age
        msg = Message(StringIO(
                "Age: bad_age\r\n"))
        meta.fixup_response_headers(msg)
        self.failUnless(msg['Age'] == '0')

    def testCacheConditionalRequest(self):
        now = utils.now()

        # if request doesn't contain If-Modified-since
        cache = Message(StringIO(
                "Date: %s\r\n"
                "Cache-control: max-age=10\r\n"
                "Content-Length: 10\r\n"
                % (FormatDate(now))))
        meta = self.metadata(FakeResponse(cache), now, now, logger)
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                ))

        self.failIf(meta.conditional_request_matches(req, cache, logger))

        # cache record doesn't contain Last-Modified
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT\r\n"
                ))

        self.failIf(meta.conditional_request_matches(req, cache, logger))

        # IF-Modified-Since, length is different
        cache = Message(StringIO(
                "Date: %s\r\n"
                "Cache-control: max-age=10\r\n"
                "Last-Modified: Mon, 09 Aug 2010 16:48:45 GMT\r\n"
                "Content-Length: 10\r\n"
                % (FormatDate(now))))

        meta = self.metadata(FakeResponse(cache), now, now, logger)

        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT; length=5\r\n"
                ))

        self.failIf(meta.conditional_request_matches(req, cache, logger))

        # IF-Modified-Since
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-Modified-Since: Mon, 09 Aug 2010 16:48:45 GMT\r\n"
                ))

        self.failUnless(meta.conditional_request_matches(req, cache, logger))

        # true if cached value is older
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-Modified-Since: Mon, 10 Aug 2010 16:48:45 GMT\r\n"
                ))

        self.failUnless(meta.conditional_request_matches(req, cache, logger))

        # if-modified-since without timezone
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-Modified-Since: Mon, 10 Aug 2010 16:48:45\r\n"
                ))

        self.failUnless(meta.conditional_request_matches(req, cache, logger))

        # etag
        cache = Message(StringIO(
                "Date: %s\r\n"
                "Cache-control: max-age=10\r\n"
                "ETag: zzzyyy\r\n"
                % (FormatDate(now))))
        meta = self.metadata(FakeResponse(cache), now, now, logger)

        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-Modified-Since: Mon, 10 Aug 2010 16:48:45\r\n"
                ))

        self.failIf(meta.conditional_request_matches(req, cache, logger))

        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-None-Match: zzzyyy\r\n"
                ))

        self.failUnless(meta.conditional_request_matches(req, cache, logger))

        # etag and last-modified
        cache = Message(StringIO(
                "Date: %s\r\n"
                "Cache-control: max-age=10\r\n"
                "ETag: zzzyyy\r\n"
                "Last-Modified: Mon, 09 Aug 2010 16:48:45 GMT\r\n"
                % (FormatDate(now))))
        meta = self.metadata(FakeResponse(cache), now, now, logger)

        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-None-Match: zzzyyy\r\n"
                ))

        self.failIf(meta.conditional_request_matches(req, cache, logger))

        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-None-Match: zzzyyy\r\n"
                "If-Modified-Since: Mon, 10 Aug 2010 16:48:45 GMT\r\n"
                ))

        self.failUnless(meta.conditional_request_matches(req, cache, logger))


    def testFreshForRequest(self):
        now = utils.now()

        cache = Message(StringIO(
                "Date: %s\r\n"
                "Cache-control: max-age=100\r\n"
                "Last-Modified: Mon, 10 Aug 2010 16:48:45 GMT\r\n"
                "Content-Length: 10\r\n"
                % (FormatDate(now))))
        meta = self.metadata(FakeResponse(cache), now, now, logger)

        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "Cache-control: unknown\r\n"
                ))

        self.failUnless(meta.fresh_for_request(now, cache, req, logger))

        # meta is expired
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                ))

        self.failIf(meta.fresh_for_request(
                now+datetime.timedelta(110), cache, req, logger))

        # no-cache
        req = Message(StringIO(
                "Cache-control: no-cache\n\r"))

        self.failIf(meta.fresh_for_request(now, cache, req, logger))

        # max-age in request
        req = Message(StringIO(
                "Cache-control: max-age=bad_value\n\r"))

        self.failUnless(meta.fresh_for_request(
                now+datetime.timedelta(seconds=11), cache, req, logger))


        req = Message(StringIO(
                "Cache-control: max-age=10\n\r"))

        self.failIf(meta.fresh_for_request(
                now+datetime.timedelta(seconds=110), cache, req, logger))

        self.failIf(meta.fresh_for_request(
                now+datetime.timedelta(seconds=11), cache, req, logger))

        # max-stale in request
        req = Message(StringIO(
                "Cache-control: max-stale=bad_value\n\r"))
        self.failUnless(meta.fresh_for_request(
                now+datetime.timedelta(seconds=10), cache, req, logger))

        req = Message(StringIO(
                "Cache-control: max-stale=10\n\r"))
        self.failIf(meta.fresh_for_request(
                now+datetime.timedelta(seconds=130), cache, req, logger))

        # min-fresh in request
        req = Message(StringIO(
                "Cache-control: min-fresh=bad_value\n\r"))
        self.failUnless(meta.fresh_for_request(
                now+datetime.timedelta(seconds=10), cache, req, logger))

        req = Message(StringIO(
                "Cache-control: min-fresh=10\n\r"))
        self.failUnless(meta.fresh_for_request(now, cache, req, logger))

        req = Message(StringIO(
                "Cache-control: min-fresh=50\n\r"))
        self.failIf(meta.fresh_for_request(
                now+datetime.timedelta(60), cache, req, logger))


class TestHTTPStorage(TestRFC2616):

    def testHTTPStorageQuery(self):
        now = utils.now()
        url  = '/test_url'

        # cache record for simple request
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"))

        expires = now + datetime.timedelta(days=365)
        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Expires: %s\r\n\r\n"
                % (FormatDate(now), FormatDate(now), FormatDate(expires))))

        meta = self.metadata(FakeResponse(resp, length=5), now, now, logger)

        key = CacheProvider.generate_key(url, req, resp)
        self.cache.set(key, (meta, 'data1'))

        nkey, nmeta, ndata = self.cache.raw_query(url, req)

        self.failUnless(key == nkey)
        self.failUnless(ndata == 'data1')

        # return file descriptor
        self.cache.data.return_files = True

        nkey, nmeta, ndata = self.cache.raw_query(url, req)

        self.failUnless(type(ndata) is file)

        ndata.close()
        self.cache.data.return_files = False

        # etag request
        req = Message(StringIO(
                "Accept-Langueg: en-ur\r\n"
                "User-Agent: Firefox\r\n"
                "If-None-Match: |test|etag||\r\n"))

        self.assertRaises(KeyError, self.cache.raw_query, url, req)

        # cache record with etag
        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Expires: %s\r\n"
                "ETag: |test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now), FormatDate(expires))))

        meta1 = self.metadata(FakeResponse(resp, length=5), now, now, logger)

        key1 = CacheProvider.generate_key(url, req, resp)
        self.cache.set(key1, (meta, 'data2'))

        nkey, nmeta, ndata = self.cache.raw_query(url, req)
        self.failUnless(key1 == nkey)
        self.failUnless(ndata == 'data2')

        # weak etag
        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "User-Agent: Firefox\r\n"
                "If-None-Match: W/|test|etag||\r\n"))

        nkey, nmeta, ndata = self.cache.raw_query(url, req)
        self.failUnless(key1 == nkey)
        self.failUnless(ndata == 'data2')

        # vary
        url1 = '/test_url1'
        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Expires: %s\r\n"
                "Vary: Accept-Language, User-Agent\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now), FormatDate(expires))))

        meta = self.metadata(FakeResponse(resp, length=5), now, now, logger)

        key2 = CacheProvider.generate_key(url1, req, resp)
        self.cache.set(key2, (meta, 'data3'))

        # should fail because request contains 'If-none-match' and
        # response doesn't contain 'Etag'
        self.assertRaises(KeyError, self.cache.raw_query, url1, req)

        # should fail because Accept-Language is different
        req = Message(StringIO(
                "Accept-Language: EN-US\r\n"
                "User-Agent: Firefox\r\n"
                "\r\n"))
        self.assertRaises(KeyError, self.cache.raw_query, url1, req)

        # should fail because Accept-Language is missing
        req = Message(StringIO(
                "User-Agent: Firefox\r\n"
                "\r\n"))
        self.assertRaises(KeyError, self.cache.raw_query, url1, req)

        # now we good
        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "User-Agent: Firefox\r\n"
                "\r\n"))

        nkey, nmeta, ndata = self.cache.raw_query(url1, req)
        self.failUnless(key2 == nkey)
        self.failUnless(ndata == 'data3')

        # combine etag and vary
        url2 = '/test_url2'
        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Expires: %s\r\n"
                "ETag: |test|etag||\r\n"
                "Vary: Accept-Language, User-Agent\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now), FormatDate(expires))))

        meta = self.metadata(FakeResponse(resp, length=5), now, now, logger)

        key4 = CacheProvider.generate_key(url2, req, resp)
        self.cache.set(key4, (meta, 'data4'))

        # should fail because: vary is matched, etag is missing
        self.assertRaises(KeyError, self.cache.raw_query, url2, req)

        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "User-Agent: Firefox\r\n"
                "If-None-Match: W/|test|etag||\r\n"
                "\r\n"))

        nkey, nmeta, ndata = self.cache.raw_query(url2, req)
        self.failUnless(key4 == nkey)
        self.failUnless(ndata == 'data4')

        # environmenterror
        def failed_load(fp):
            raise EnvironmentError("Test failure")

        old_load = self.cache.data._load_
        self.cache.data._load_ = failed_load

        self.assertRaises(KeyError, self.cache.raw_query, url2, req)

        self.cache.data._load_ = old_load

        # remove keys
        meta, data = self.cache.raw_get(key4)
        self.cache.data.del_keys(self.cache, url2, req)
        self.assertRaises(KeyError, self.cache.raw_get, key4)

        keys = ('/test_url|*|~', '/test_url|fHRlc3R8ZXRhZ3x8|~')
        for key in keys:
            meta, data = self.cache.raw_get(key)

        self.cache.data.del_url(self.cache, url)
        for key in keys:
            self.assertRaises(KeyError, self.cache.raw_get, key)


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    return suite
