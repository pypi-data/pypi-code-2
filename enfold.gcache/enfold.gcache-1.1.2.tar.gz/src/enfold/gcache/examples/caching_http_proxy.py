# $Id: caching_http_proxy.py 4414 2010-10-08 15:24:18Z nikolay $
# Copyright: Enfold Systems, LLC

# A sample socket server that proxies some external site, but caches the content
import sys
import BaseHTTPServer
import httplib
import os
import time
import rfc822
import cStringIO as StringIO

from enfold.gcache import Cache, metadata, Uncachable
from enfold.gcache.httpcache import Storage, CacheProvider, get_time_header

# Short timeout so Ctrl+C terminates the program and allows the cache to
# flush itself.
import socket
socket.setdefaulttimeout(3)

cache = None

# This is setup to test Zope, so creates a new URL that the Zope VHM
# understands.
def CalculateVHM(url, lh_root, lh_server, lh_port,
                      vh_root, vh_server, vh_port,
                      lh_scheme = "http", vh_scheme = "http"):
    product_url = url[len(lh_root)+1:]
#        url = "%s://%s:%s/" % (lh_scheme, lh_server, lh_port)

    url = vh_scheme + "://" + vh_server
    if vh_port:
        url += ":%s" % (vh_port,)
    def urljoin(start, end):
        # I hate urlparse :)
        if start.endswith("/"):
            start = start[:-1]
        if end.startswith("/"):
            end = end[1:]
        return start + "/" + end

    url = urljoin(url, "VirtualHostBase")
    url = urljoin(url, lh_scheme)
    url = urljoin(url, lh_server + ':' + lh_port)
    url = urljoin(url, vh_root)
    url = urljoin(url, "VirtualHostRoot")

    bits = [bit for bit in lh_root.split("/") if bit]
    for bit in bits:
        url = urljoin(url, "_vh_" + bit)
    url = urljoin(url, product_url)
    return url


class CachingHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        new_url = CalculateVHM(self.path,
                               lh_root = "",
                               vh_root = "",
                               lh_server = 'localhost',
                               vh_server = 'localhost',
                               lh_port = "8888",
                               vh_port = "8080")
        try:
            meta, d=cache[new_url]
            ims = get_time_header(self.headers, 'if-modified-since')
            if ims and meta.t_modified <= ims:
                print "Sending 304 response"
                self.send_response(304)
                # Send just the headers with a 304.
                msg = rfc822.Message(StringIO.StringIO(d))
                exp = meta.get_new_expiry_value()
                if exp is not None:
                    msg["Expires"] = exp
                self.wfile.write(str(msg) + "\r\n")
            else:
                # The entire file with a 200, plus possibly an expiry
                self.send_response(200)
                exp = meta.get_new_expiry_value()
                if exp is not None:
                    self.send_header("Expires", exp)
                self.wfile.write(d)
        except Uncachable, error:
            resp = error[0]
            print "uncachable - sending manually"
            self.send_response(resp.status, resp.reason)
            for line in resp.msg.headers:
                self.wfile.write(line)
            self.wfile.write(resp.read())
        print str(cache.stats)

def go(proxy_site, cache_dir):
    global cache
    print "Cache is at", cache_dir
    cache = Cache(storage = Storage(cache_dir),
                  provider = CacheProvider(proxy_site),
                  default_age = 600,
                  max_size = 5000000)

    try:
        try:
            BaseHTTPServer.test(HandlerClass=CachingHTTPHandler)
        except KeyboardInterrupt:
            print "Interrupted"
    finally:
        print str(cache.stats)
        cache.close()

def run():
    import shutil, tempfile
    dirname = "TestCache"
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    go("driblette:8080", dirname)

if __name__=='__main__':
    run()
