################################################################################
#
# Copyright (c) 2010 Enfold Systems, LLC
# All Rights Reserved.
#
# HTTP CacheProvider
#
# $Id: httpcacheprovider.py 4292 2010-08-30 19:57:37Z nikolay $
#
################################################################################
import httplib, socket, base64
from cPickle import loads, dumps

from zope import interface

from interfaces import IHTTPCacheProvider
from interfaces import \
    Uncachable, ValidationError, ValidationGotNewItem, HTTPValidationError

from utils import now, log_headers, cleanup_hop_headers


class HTTPCacheProviderBase(object):
    interface.implements(IHTTPCacheProvider)

    metadataFactory = None

    def __init__(self, logger):
        self.logger = logger

    def provide(self, key):
        raise NotImplementedError("provide")

    def validate(self, key, meta, data, *args, **kw):
        raise NotImplementedError("validate")

    @classmethod
    def generate_key(cls, url, request, response):
        key = [url]

        # etag
        etag = response.get('etag', '')
        if etag.startswith('W'):
            etag = etag[2:]

        if etag:
            key.append(base64.b64encode(etag))
        else:
            key.append('*')

        # vary
        vary = {}
        for hdr in response.get('vary', '').split(','):
            hdr = hdr.strip().lower()
            if hdr in request:
                vary[hdr] = request.get(hdr).strip()

            if hdr == '*':
                raise Uncachable("Response contains 'Vary: *'")

        if vary:
            key.append(base64.b64encode(dumps(vary, 2)))
        else:
            key.append('~')

        return '|'.join(key)

    @classmethod
    def parse_key(cls, key):
        try:
            url, etag, vary = key.split('|', 3)
        except ValueError:
            return key, '', {}

        if etag == '*':
            etag = ''
        else:
            etag = base64.b64decode(etag)

        if vary == '~':
            vary = {}
        else:
            vary = loads(base64.b64decode(vary))

        return url, etag, vary

    def open_host(self, scheme, host, port=None):
        if scheme == 'http':
            return httplib.HTTPConnection(host, port)
        elif scheme == 'https':
            return httplib.HTTPSConnection(host, port)

        raise ValueError('Only http or https supported')

    def done_with_host(self, connection, response):
        """ response may be None, but connection will never be """
        if response is not None:
            response.close()
        connection.close()

    def host_failed(self, connection):
        """ do nothing by default """
        pass

    def do_provide(self, schema, host, key):
        url, etag, vary = self.parse_key(key)

        resp = None
        request_time = now()
        try:
            c = self.open_host(schema, host)
            c.putrequest("GET", url)
            c.endheaders()
            resp = c.getresponse()
        except Exception, exc:
            self.host_failed(c)
            raise Uncachable(str(exc))
        finally:
            self.done_with_host(c, resp)

        metadata = self.metadataFactory(
            resp, request_time, now(), self.logger)

        bits = cleanup_hop_headers(resp)
        bits.append('') # blank line after headers.
        bits.append(resp.read())
        # We keep more than just the content, so content-length doesn't help.
        data = "\r\n".join(bits)
        metadata.size = len(data)

        key = self.generate_key(url, {}, resp.msg)

        return key, metadata, data

    def do_validate(self, scheme, host, key, meta, data, request=None):
        logger = self.logger

        # XXX - we also need to get a little smarter re fully-qualified-URLs etc
        if not isinstance(data, basestring):
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
            raise ValidationError(key)

        url, etag, vary = self.parse_key(key)
        server_modified, _ = meta.get_meta_header('last-modified')

        if not etag and not server_modified:
            logger.debug(
                "Can't revalidate '%s/%s' - no Last-Modified or ETag", host, url)
            raise ValidationError(url)

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

                if request is None:
                    request = {}

                # ie, the *entire* set of client headers should be sent. This
                # is also necessary to make sense of 'Vary: *'
                for header_name in request.keys():
                    vals = request.getheaders(header_name)
                    c.putheader(header_name, ",".join(vals))

                if server_modified and \
                        (not request or 'if-modified-since' not in request):
                    c.putheader("If-Modified-Since", server_modified)
                    logger.debug(
                        "Adding header If-Modified-Since: %s", server_modified)

                c.endheaders()

                resp = c.getresponse()

                # Anything other than 200 or 304 is thrown away again
                logger.info(
                    "Validate response %s: %s (%s)", resp.status,resp.reason,url)

                log_headers(logger, resp, "Validate response headers")

                if resp.status == 200:
                    metadata = self.metadataFactory(
                        resp, request_time, now(), logger)

                    bits = cleanup_hop_headers(resp)
                    bits.append('') # blank line after headers.
                    bits.append(resp.read())

                    data = "\r\n".join(bits)
                    metadata.size = len(data)

                    key = self.generate_key(url, request, resp.msg)
                    raise ValidationGotNewItem(key, metadata, data)

                if resp.status != 304:
                    raise HTTPValidationError(key)

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

                # need check newly generated key
                meta.update_from_response(resp, request_time, now(), logger)

                if meta.size == -1: # no content-length supplied
                    meta.size = old_size
                elif meta.size != old_size:
                    logger.info("Ignoring 304 validation response with incorrect"
                                " content-length (old size %s, new size %s)",
                                old_size, meta.size)
                    raise ValidationError(key)

                # server return 304, but etag or vary is changed
                if key != self.generate_key(url, request, resp.msg):
                    raise HTTPValidationError(key)

                # metadata looks good so we are happy.
                return meta

            except (socket.error, httplib.error):
                self.host_failed(c)
                # Note: socket or httplib errors here
                # should be caught by the caller.
                # We do *not* want to flag the item as stale simply because the
                # origin site is down - the caller has a better idea than us about
                # what the 'right thing' to do is there...
                # so throw it back up
                raise
        finally:
            self.done_with_host(c, resp)


class HTTPCacheProvider(HTTPCacheProviderBase):
    """ A cache provider that serves a single host,
    and uses the URL directly as a key. """

    def __init__(self, schema, host, logger = None):
        super(HTTPCacheProvider, self).__init__(logger)

        self.schema = schema
        self.host = host

    def provide(self, key):
        return self.do_provide(self.schema, self.host, key)

    def validate(self, key, meta, data, *args, **kw):
        return self.do_validate(
            self.schema, self.host, key, meta, data, *args, **kw)
