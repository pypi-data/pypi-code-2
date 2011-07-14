# -*- coding: UTF-8 -*-
"""Request filter to handle multipart uploads from buggy Flash clients."""

__all__ = [
    'SafeMultipartFilter',
    'MultipartWrapper',
]

import logging
import re

import cherrypy
from turbogears import config


log = logging.getLogger('turbogears.filters')


# Taken from http://www.cherrypy.org/ticket/648
class MultipartWrapper(object):
    r"""Wraps a file-like object, returning '' when Content-Length is reached.

    The cgi module's logic for reading multipart MIME messages doesn't
    allow the parts to know when the Content-Length for the entire message
    has been reached, and doesn't allow for multipart-MIME messages that
    omit the trailing CRLF (Flash 8's FileReference.upload(url), for example,
    does this). The read_lines_to_outerboundary function gets stuck in a loop
    until the socket times out.

    This rfile wrapper simply monitors the incoming stream. When a read is
    attempted past the Content-Length, it returns an empty string rather
    than timing out (of course, if the last read *overlaps* the C-L, you'll
    get the last bit of data up to C-L, and then the next read will return
    an empty string).

    """
    def __init__(self, rfile, clen):
        self.rfile = rfile
        self.clen = clen
        self.bytes_read = 0

    def read(self, size=None):
        if self.clen:
            # Return '' if we've read all the data.
            if self.bytes_read >= self.clen:
                return ''

            # Reduce 'size' if it's over our limit.
            new_bytes_read = self.bytes_read + size
            if new_bytes_read > self.clen:
                size = self.clen - self.bytes_read

        data = self.rfile.read(size)
        self.bytes_read += len(data)
        return data

    def readline(self, size=None):
        if size is not None:
            if self.clen:
                # Return '' if we've read all the data.
                if self.bytes_read >= self.clen:
                    return ''

                # Reduce 'size' if it's over our limit.
                new_bytes_read = self.bytes_read + size
                if new_bytes_read > self.clen:
                    size = self.clen - self.bytes_read

            data = self.rfile.readline(size)
            self.bytes_read += len(data)
            return data

        # User didn't specify a size ...
        # We read the line in chunks to make sure it's not a 100MB line !
        res = []
        size = 256
        while True:
            if self.clen:
                # Return if we've read all the data.
                if self.bytes_read >= self.clen:
                    return ''.join(res)

                # Reduce 'size' if it's over our limit.
                new_bytes_read = self.bytes_read + size
                if new_bytes_read > self.clen:
                    size = self.clen - self.bytes_read

            data = self.rfile.readline(size)
            self.bytes_read += len(data)
            res.append(data)
            # See http://www.cherrypy.org/ticket/421
            if len(data) < size or data[-1:] == "\n":
                return ''.join(res)

    def readlines(self, sizehint=0):
        # Shamelessly stolen from StringIO
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()
        return lines

    def close(self):
        self.rfile.close()

    def __iter__(self):
        return self.rfile

    def next(self):
        if self.clen:
            # Return '' if we've read all the data.
            if self.bytes_read >= self.clen:
                return ''

        data = self.rfile.next()
        self.bytes_read += len(data)
        return data


class SafeMultipartFilter:
    """CherryPy filter to handle buggy multipart requests from Flash clients."""

    flash_ua_rx = re.compile(r'(Shockwave|Adobe)\s+Flash.*')

    def before_request_body(self):
        if not config.get("safempfilter.on", False):
            return
        log.debug("Using FlashMultipartFilter for request %s.",
            cherrypy.request.path)
        ct = cherrypy.request.headers.get('Content-Type', '')
        ua = cherrypy.request.headers.get('User-Agent', '')

        if ct.startswith('multipart/') and self.flash_ua_rx.match(ua):
            log.debug("Detected Flash client multipart request. "
                "Using MulipartWrapper to read request")
            clen = cherrypy.request.headers.get('Content-Length', '0')
            try:
                clen = int(clen)
            except ValueError:
                return
            cherrypy.request.rfile = MultipartWrapper(
                cherrypy.request.rfile, clen)
