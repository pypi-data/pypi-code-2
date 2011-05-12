# LinkExchange - Universal link exchange service client
# Copyright (C) 2009-2011 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import sys
import os
import tempfile
import urllib
import urlparse
import datetime
import re
import signal
import socket
import time
try:
    import subprocess
except ImportError:
    subprocess = None

from linkexchange.clients import PageRequest
from linkexchange.utils import find_links

class MultiHashDriverTestMixin:
    """
    Implements tests for multihash driver API methods.
    """

    with_blocking = True

    def test_load(self):
        self.assertRaises(KeyError, self.db.load, 'notexists')
        self.db.save('testkey', [('k1', 'v1'), ('k2', 'v2')])
        hash = self.db.load('testkey')
        self.assertEqual(hash['k1'], 'v1')
        self.assertEqual(hash['k2'], 'v2')

    def test_get_mtime(self):
        def round_dt(dt):
            return dt.replace(microsecond=0)
        self.assertRaises(KeyError, self.db.get_mtime, 'notexists')
        t1 = round_dt(datetime.datetime.now())
        self.db.save('testkey',
                [('k%d' % i, 'v%d' % i) for i in range(100)])
        t2 = round_dt(datetime.datetime.now())
        mt = round_dt(self.db.get_mtime('testkey'))
        self.assertEqual(t1 <= mt <= t2, True)

    def test_modify(self):
        self.db.save('testkey', [('k1', 'v1'), ('k2', 'v2')])
        self.db.modify('testkey', [('k2', 'v2x')])
        hash = self.db.load('testkey')
        self.assertEqual(hash['k1'], 'v1')
        self.assertEqual(hash['k2'], 'v2x')

    def test_delete(self):
        self.db.save('testkey', [('k1', 'v1'), ('k2', 'v2')])
        self.db.delete('testkey', ['k2'])
        hash = self.db.load('testkey')
        self.assertEqual(len(hash), 1)

    def test_blocking(self):
        def test_generator():
          for i in range(100):
            if i == 5:
              result = self.db.save('testkey', dict(bar=3),
                      blocking=False)
              if self.with_blocking:
                  self.assertEqual(result, False)
              else:
                  self.assertEqual(result, True)
            yield ('bar%d' % i, i)
        result = self.db.save('testkey', test_generator())
        self.assertEqual(result, True)
        hash = self.db.load('testkey')
        self.assertEqual(hash['bar55'], 55)

class SimpleFileTestServer(object):
    """
    Simple test server that stores data in file on file system and sets url
    attribute that points to it.
    """

    filename = None
    raw_data = ''

    def __init__(self, filename=None, raw_data=None):
        if filename:
            self.filename = filename
        if self.filename:
            fo = open(self.filename, 'w')
        else:
            fd, self.filename = tempfile.mkstemp()
            fo = os.fdopen(fd, 'w')
        if raw_data is not None:
            self.raw_data = raw_data
        fo.write(self.raw_data)
        path = urllib.pathname2url(os.path.realpath(self.filename))
        self.url = urlparse.urlunsplit(('file', '', path, '', ''))
        self._unlink = os.unlink

    def __del__(self):
        try:
            self._unlink(self.filename)
        except OSError:
            pass

class ClientBaseTestMixin:
    host = 'example.com'
    bot_ip = '123.45.67.89'
    cookies = None

    def create_servers(cls):
        raise NotImplementedError()
    create_servers = classmethod(create_servers)

    def setUpClass(cls):
        cls.servers = cls.create_servers()
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        del cls.servers
    tearDownClass = classmethod(tearDownClass)

    def new_client(self, **kw):
        raise NotImplementedError()

    def new_request(self, **kw):
        kw.setdefault('host', self.host)
        kw.setdefault('remote_addr', self.bot_ip)
        kw.setdefault('cookies', self.cookies)
        return PageRequest(**kw)

class ClientLinksTestMixin(ClientBaseTestMixin):
    page_link_map = {
            '/':[
                ('http://example1.com/', 'example text 1'),
                ]}
    check_code = ''
    html_links_link_pattern = (r'<a[^>]+?href="(?P<href>[^"]+)"[^>]*>'
            '(?P<anchor>[^<>]+?)</a>')
    html_links_delim_pattern = None

    def test_links_get_raw_links(self):
        client = self.new_client()
        for test_uri, test_links in self.page_link_map.items():
            request = self.new_request(uri=test_uri)
            raw_links = client.get_raw_links(request)
            self.assertEqual(len(raw_links), len(test_links))
            for i in range(len(test_links)):
                test_href, test_anchor = test_links[i]
                attrs, anchor = find_links(raw_links[i])[0]
                self.assertEqual(attrs.get('href', ''), test_href)
                self.assertEqual(anchor.strip(), test_anchor.strip())

    def test_links_get_html_links(self):
        client = self.new_client()
        link_re = re.compile(self.html_links_link_pattern)
        if self.html_links_delim_pattern:
            delim_re = re.compile(self.html_links_delim_pattern)
        else:
            delim_re = None

        for test_uri, test_links in self.page_link_map.items():
            request = self.new_request(uri=test_uri)
            html = client.get_html_links(request)
            links = list(link_re.finditer(html))
            self.assertEqual(len(links), len(test_links))
            for i in range(len(links)):
                test_href, test_anchor = test_links[i]
                self.assertEqual(links[i].group('href'), test_href)
                self.assertEqual(links[i].group('anchor'), test_anchor)
                if i > 0 and delim_re:
                    delim_found = delim_re.search(html,
                            links[i-1].end(), links[i].start()) is not None
                    self.assertEqual(delim_found, True)

    def test_links_check_code(self):
        client = self.new_client()
        request = self.new_request(uri='/not_exists')
        self.assertEqual(
                self.check_code in client.get_raw_links(request)[0], True)

    def test_links_broken_server(self):
        client = self.new_client(broken_server=True)
        for test_uri, test_links in self.page_link_map.items():
            request = self.new_request(uri=test_uri)
            raw_links = client.get_raw_links(request)
            self.assertEqual(raw_links, [])

class ClientContentFilterTestMixin(ClientBaseTestMixin):
    page_content_map = {
            '/': [
                ('Some text content.', 'Some text content filtered.'),
                ],
            }

    def test_content_filter(self):
        client = self.new_client()
        for test_uri, test_content_list in self.page_content_map.items():
            request = self.new_request(uri=test_uri)
            for test_content in test_content_list:
                filtered = client.content_filter(
                        request, test_content[0])
                self.assertEqual(filtered, test_content[1])

def _wait_socket(addr, timeout=10):
    t = time.time()
    while True:
        try:
            s = socket.socket()
            s.connect(addr)
        except socket.error:
            pass
        else:
            s.close()
            return True
        if time.time() - t > timeout:
            return False
        time.sleep(1)

class _WebAppSubProcess(object):
    def __init__(self, args, addr):
        kw = {}
        if sys.platform != 'win32':
            kw['preexec_fn'] = os.setpgrp
        self._proc = subprocess.Popen(args, **kw)
        _wait_socket(addr)

    def terminate(self):
        if sys.platform != 'win32':
            os.killpg(self._proc.pid, signal.SIGTERM)
        else:
            os.system("taskkill /F /T /PID %d" % self._proc.pid)

    def wait(self):
        return self._proc.wait()

class _WebAppUnixProcess(object):
    def __init__(self, args, addr):
        self.pid = os.fork()
        if not self.pid:
            os.setpgrp()
            os.execvp(args[0], args)
            sys.exit(1)
        _wait_socket(addr)

    def terminate(self):
        os.killpg(self.pid, signal.SIGTERM)

    def wait(self):
        pid, status = os.waitpid(self.pid, 0)
        return status << 8

if subprocess is not None:
    WebAppProcess = _WebAppSubProcess
else:
    WebAppProcess = _WebAppUnixProcess
