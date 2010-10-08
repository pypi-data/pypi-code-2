# Test the cache semantics described in RFC2616.
"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import unittest
import time, datetime, base64
from rfc822 import Message
from cPickle import loads
from cStringIO import StringIO
from enfold.gcache import utils, httpcache
from enfold.gcache.interfaces import \
    Uncachable, ValidationError, HTTPValidationError
from enfold.gcache.httpcacheprovider import HTTPCacheProviderBase

from testRFC2616 import CacheProvider
from testRFC2616 import logger, FormatDate, FakeResponse, TestRFC2616


class TestHTTPProvider(TestRFC2616):

    def testGenerateKey(self):
        now = utils.now()
        url  = '/test_url'
        bprovider = HTTPCacheProviderBase(logger)

        self.assertRaises(NotImplementedError, bprovider.provide, url)
        self.assertRaises(NotImplementedError, bprovider.validate, url,None,None)

        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                % (FormatDate(now), FormatDate(now))))

        key = bprovider.generate_key(url, {}, resp)

        _url, _etag, _vary = key.split('|')
        self.failUnless(_url == url)
        self.failUnless(_etag == '*')
        self.failUnless(_vary == '~')

        # cache record with etag
        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "ETag: |test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now))))

        key = bprovider.generate_key(url, {}, resp)

        _url, _etag, _vary = key.split('|')
        self.failUnless(_url == url)
        self.failUnless(_etag == base64.b64encode('|test|etag||'))
        self.failUnless(_vary == '~')

        # cache record with vary
        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "User-Agent: Firefox\r\n"))

        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Vary: Accept-Language, User-Agent\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now))))

        key = bprovider.generate_key(url, req, resp)

        _url, _etag, _vary = key.split('|')
        _vary = loads(base64.b64decode(_vary))
        self.failUnless(_url == url)
        self.failUnless(_etag == '*')
        self.failUnless(_vary == {'accept-language': 'en-us', 'user-agent': 'Firefox'})

        # cache record with etag and vary
        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "User-Agent: Firefox\r\n"))

        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Vary: Accept-Language, User-Agent\r\n"
                "ETag: W/|test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now))))

        key = bprovider.generate_key(url, req, resp)

        _url, _etag, _vary = key.split('|')
        _vary = loads(base64.b64decode(_vary))
        self.failUnless(_url == url)
        self.failUnless(_etag == base64.b64encode('|test|etag||'))
        self.failUnless(_vary == {'accept-language': 'en-us', 'user-agent': 'Firefox'})

        # uncachable response
        resp = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Vary: *\r\n\r\n"
                % (FormatDate(now), FormatDate(now))))

        self.assertRaises(
            Uncachable, bprovider.generate_key, url, req, resp)

        # parse key
        _url, _etag, _vary = bprovider.parse_key(url)
        self.failUnless(_url == url)
        self.failUnless(_etag == '')
        self.failUnless(_vary == {})


        _url, _etag, _vary = bprovider.parse_key('/test_url|*|~')
        self.failUnless(_url == url)
        self.failUnless(_etag == '')
        self.failUnless(_vary == {})

        _url, _etag, _vary = bprovider.parse_key(key)
        self.failUnless(_url == url)
        self.failUnless(_etag == '|test|etag||')
        self.failUnless(_vary == {'accept-language': 'en-us', 'user-agent': 'Firefox'})

    def testProvide(self):
        now = utils.now()
        url  = '/test_url'

        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Vary: Accept-Language, User-Agent\r\n"
                "ETag: W/|test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now))))

        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", 3, 'foo'), None))

        key = self.cache.provider.generate_key(url, {}, msg)
        self.cache.get(url)

        self.assertRaises(
            KeyError, self.cache.data.get_meta, url)

        meta, data = self.cache.raw_get(key)
        self.failUnless(isinstance(meta, httpcache.httpmetadata))
        self.failUnless('foo' in data)

        # Uncachable
        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", None, 'foo'),))

        self.assertRaises(
            Uncachable, self.cache.get, '/test_url1')

        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Vary: *\r\n"
                "ETag: W/|test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now))))

        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", 3, 'foo'), None))

        self.assertRaises(
            Uncachable, self.cache.get, '/test_url1')

    def testValidate(self):
        now = utils.now()
        url  = '/test_url'

        # exceptions
        msg = Message(StringIO(
                "Date: %s\r\n"
                "\r\n"
                % (FormatDate(now))))

        meta = self.metadata(FakeResponse(msg, length=3), now, now, logger)
        data = StringIO("404 asasdasd")

        # cache validate non 200 pages
        self.assertRaises(
            ValidationError, self.cache.provider.validate,'/test_url', meta, data)

        # no etag or last-modified
        data = "200 OK"
        self.assertRaises(
            ValidationError, self.cache.provider.validate,'/test_url', meta, data)

        # create record in cache
        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now-datetime.timedelta(days=1)))))

        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", 3, 'foo'), None))

        key1 = self.cache.provider.generate_key(url, {}, msg)
        data1 = self.cache.get(url)

        meta, data = self.cache.raw_get(key1)

        self.failUnless(data == data1)

        # validation error if we get somthing different from 200 or 304
        self.provider_responses.append(
            (FakeResponse(msg, 404, "Not Found", None, 'foo'), None))

        self.assertRaises(
            ValidationError, self.cache.provider.validate,'/test_url', meta, data)

        # Uncachable
        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "\r\n"))

        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "Vary: *\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now-datetime.timedelta(days=1)))))

        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", 3, 'foo'), None))

        self.assertRaises(
            Uncachable,
            self.cache.validate_item, now, key1, meta, data, None, req)

        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", None, 'foo'), None))

        self.assertRaises(
            Uncachable,
            self.cache.validate_item, now, key1, meta, data,
            self.cache.provider.validate, req)

        # ValidationGotNewItem
        req = Message(StringIO(
                "Accept-Language: en-us\r\n"
                "\r\n"))

        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "ETag: |test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now-datetime.timedelta(days=1)))))

        self.cache.provider.host = 'localhost', 80
        self.provider_responses.append(
            (FakeResponse(msg, 200, "OK", 3, 'foo'), None))

        self.cache.validate_item(now, key1, meta, data, None, req)

        # key is changed
        self.assertRaises(KeyError, self.cache.raw_get, key1)

        key2 = self.cache.provider.generate_key(url, {}, msg)
        meta, data = self.cache.raw_get(key2)

        # can't validate 304 response if content length is different
        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "ETag: |test|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now-datetime.timedelta(days=1)))))

        self.provider_responses.append(
            (FakeResponse(msg, 304, "OK", 3, 'foo'), None))

        self.assertRaises(
            ValidationError,
            self.cache.provider.validate, key2, meta, data)

        # can't validate 304 response if etag or vary are changed
        msg = Message(StringIO(
                "Date: %s\r\n"
                "Last-Modified: %s\r\n"
                "ETag: |test2|etag||\r\n"
                "\r\n"
                % (FormatDate(now), FormatDate(now-datetime.timedelta(days=1)))))

        self.provider_responses.append(
            (FakeResponse(msg, 304, "OK", 3, 'foo'), None))

        self.assertRaises(
            HTTPValidationError,
            self.cache.provider.validate, key2, meta, data)


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    return suite
