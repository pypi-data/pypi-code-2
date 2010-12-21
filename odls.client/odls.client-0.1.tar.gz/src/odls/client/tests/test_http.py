##
## test_http.py
## Login : <uli@pu.smp.net>
## Started on  Tue Aug 10 16:17:01 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Test HTTP stuff.
"""
import os
import shutil
import tempfile
import unittest
import urllib2
from cStringIO import StringIO
from pysqlite2 import dbapi2 as sqlite3
from ulif.pynotify import ADDED, MODIFIED, DELETED, FILE_TYPE
from ulif.pynotify.base import FSChange
from ulif.pynotify.sqlite import SQLiteFSWalker as FSWalker
from odls.client.http import (extended_opener, ODLSHTTPClient,
                              get_content_type)
from odls.client.tests.testing import ODLSServer, SERVER, DEFAULT_OPENER
from odls.client.tests.test_configuration import create_custom_conf

class FakeChange(object):
    """A faked change.
    """

    def __init__(self, path=None):
        self.path = path
        self.basename = os.path.basename(path)
        self.filetype = FILE_TYPE
        self.changetype = MODIFIED

class FakeResponse(object):
    """A faked successful response from server.
    """
    code = 200
    body = 'auth OK, write OK\n'

    def __init__(self, *args, **kw):
        self._body = StringIO()
        self._body.write(self.body)
        self._body.seek(0)
        return

    def read(self):
        return self._body.read()

    def readlines(self):
        return self._body.readlines()

    def seek(self, pos):
        return self._body.seek(pos)

class FakeBadResponse(FakeResponse):
    """A faked response that indicates server problems.
    """
    body = 'auth OK, write FAILED\n'
    
class HTTPTestBase(unittest.TestCase):

    def setUp(self):
        self.server_url = 'localhost:8080'
        self.server_username = 'test'
        self.server_password = 'test'
        self.workdir = tempfile.mkdtemp()
        self.dbfile = os.path.join(self.workdir, 'custom.db')
        self.ini_path = os.path.join(self.workdir, 'custom.ini')
        self.filepath = os.path.join(self.workdir, 'files')
        self.samplefilepath = os.path.join(self.filepath, 'sample.txt')
        self.fake_change = FakeChange(self.samplefilepath)
        
        os.mkdir(self.filepath)
        open(self.samplefilepath, 'wb').write(
            "Some sample file\n")
        self.opener =  extended_opener(
            host=self.server_url,
            username=self.server_username,
            password=self.server_password)
        self.createCustomConf()
        self.createFakeApp()
        self.walker = FSWalker(self.dbfile) # Creates DB tables
        return

    def createCustomConf(self, defaults={}):
        local_defaults = dict(
            server_url='http://localhost:8080/echo',
            http_username='test',
            http_username_prefix='',
            http_pw='test',
            http_pw_prefix='',
            watch_folders=self.filepath,
            watch_ignore_odls_failure='no', # This is non-default!
            dbfile=self.dbfile,
            )
        defaults.update(local_defaults)
        create_custom_conf(
            self.ini_path, defaults=defaults
            )
        return
        
    
    def createFakeApp(self, argv=None):
        if argv == None:
            argv = ['-c', self.ini_path]
        self.app = object()
        from odls.client.configuration import ODLSConfiguration
        config = ODLSConfiguration(argv=argv)
        class FakeApp(object):
            config = None
            logger = None
        self.app = FakeApp()
        self.app.config = config
        return

    def tearDown(self):
        self.walker.conn.close()
        # This is not clean. However, on Windows we cannot remove
        # trees due to process restrictions during tests.
        try:
            shutil.rmtree(self.workdir)
        except:
            pass
        return

class HTTPServerlessTest(HTTPTestBase):
    """HTTP tests that do not require a running server.
    """

    def setUp(self):
        super(HTTPServerlessTest, self).setUp()
        self.sent = []
        self.unsent = []
        return

    def sendChangeReplacement(self, change):
        """Replacement method for ODLSHTTPClient.sendChange.

        This method mimics a not successful send action.
        """
        self.unsent.append(change)
        return None
    
    def sendChangeSuccessfully(self, change):
        """Replacement method for ODLSHTTPClient.sendChange.

        This method mimics a successful send action.
        """
        self.sent.append(change)
        return FakeResponse()

    def sendChangeFailing(self, change):
        """Replacement method for ODLSHTTPClient.sendChange.

        This method mimics a successfull connect with failed server
        result (no 'auth OK, write OK').
        """
        self.unsent.append(change)
        return FakeBadResponse()

    def getNumUnseen(self):
        """Get number of entries in ``unseen`` table.
        """
        num_unseen = self.walker.conn.execute(
            "SELECT count(*) FROM seenchanges WHERE 1=1")
        return [x for x in num_unseen][0][0]
        
    def tearDown(self):
        super(HTTPServerlessTest, self).tearDown()
        return

    def test_get_content_type(self):
        result0 = get_content_type('foo', content_type='bar')
        self.assertEqual(result0, 'bar')
        testfile1 = os.path.join(self.workdir, 'mytestfile1')
        open(testfile1, 'wb').write('Hello')
        testfile2 = os.path.join(self.workdir, 'mytestfile2.txt')
        open(testfile2, 'wb').write('Hello')
        result1 = get_content_type(testfile1)
        result2 = get_content_type(testfile2)
        self.assertEqual(result1, 'application/octet-stream')
        self.assertEqual(result2, 'text/plain')

    def test_stop(self):
        # XXX: This test does not make much sense.
        #      It only pleases the coverage report.
        client = ODLSHTTPClient(self.app)
        client.stop()

    def test_send_empty_change_no_server(self):
        """Make sure we get ``None`` if server does not respond.
        """
        client = ODLSHTTPClient(self.app)
        response = client.sendChange(self.fake_change)
        self.assertTrue(response is None)

    def test_send_changes(self):
        client = ODLSHTTPClient(self.app)
        changes = self.walker.walk(self.app.config.options.dbfile)
        client.sendChange = self.sendChangeSuccessfully
        client.sendChanges(changes)
        self.assertEqual(len(self.sent), 1)
        num_unseen = self.getNumUnseen()
        self.assertEqual(num_unseen, 0)
        return

    def test_send_changes_bad_reply(self):
        client = ODLSHTTPClient(self.app)
        changes = self.walker.walk(self.app.config.options.dbfile)
        client.sendChange = self.sendChangeFailing
        client.sendChanges(changes)
        self.assertEqual(len(self.sent), 0)
        num_unseen = self.getNumUnseen()
        self.assertEqual(num_unseen, 1)
        return

    def test_send_changes_skip_directories(self):
        client = ODLSHTTPClient(self.app)
        dir = os.path.join(self.filepath, 'sampledir')
        os.mkdir(dir)
        changes = list(self.walker.walk(self.filepath))
        client.sendChange = self.sendChangeSuccessfully
        self.assertTrue(dir in [x.path for x in changes])
        client.sendChanges(changes)
        self.assertFalse(dir in [x.path for x in self.sent])
        return

    def test_send_changes_no_server(self):
        client = ODLSHTTPClient(self.app)
        self.walker.execute(
            self.walker.conn.cursor(),
            "REPLACE INTO filechanges(path,status) VALUES (?,?)",
            (self.samplefilepath, 0)
            )
        change = FSChange(self.samplefilepath, ADDED)
        response = client.sendChanges([change])
        self.assertTrue(response is None)

        num_unseen = self.getNumUnseen()
        self.assertEqual(num_unseen, 1)

    def test_send_unsent_changes(self):
        client = ODLSHTTPClient(self.app)
        changes = self.walker.walk(self.filepath)
        client.sendChange = self.sendChangeReplacement
        client.sendChanges(changes)

        client.sendChange = self.sendChangeSuccessfully
        client.sendUnsentChanges()
        self.assertEqual(len(self.sent), 1)
        
        num_unseen = self.getNumUnseen()
        self.assertEqual(num_unseen, 0)
        return
        
    def test_send_unsent_changes_no_server(self):
        client = ODLSHTTPClient(self.app)
        changes = self.walker.walk(self.filepath)
        client.sendChange = self.sendChangeReplacement
        client.sendChanges(changes)
        client.sendUnsentChanges()

        num_unseen = self.getNumUnseen()
        self.assertEqual(num_unseen, 2)
        return
        
    def test_send_unsent_changes_wo_filechangetable(self):
        client = ODLSHTTPClient(self.app)
        cur = self.walker.conn.cursor()
        self.walker.execute(cur, "DROP TABLE filechanges")
        # fail if that raises some exception....
        result = client.sendUnsentChanges()
        self.assertTrue(result is None)
        return

    def test_respect_nohttp(self):
        self.app.config.options.nohttpout = True
        client = ODLSHTTPClient(self.app)
        change = FakeChange('/foo/bar')
        changes = [change,]
        client.sendChange = self.sendChangeReplacement
        client.sendChanges(changes)
        client.sendUnsentChanges()
        self.assertEqual(self.sent, [])
        self.assertEqual(self.unsent, [])

    def test_respect_watch_ignore_odls_failure(self):
        self.app.config.options.watch_ignore_odls_failure = True
        client = ODLSHTTPClient(self.app)
        changes = self.walker.walk(self.app.config.options.dbfile)
        change = FakeChange('/foo/bar')
        client.sendChange = self.sendChangeFailing
        client.sendChanges(changes)
        num_unseen = self.getNumUnseen()
        self.assertEqual(num_unseen, 0)

    def test_get_data(self):
        client = ODLSHTTPClient(self.app)
        result = client.getData(self.fake_change)
        self.assertTrue('file_info[fsize]' in [x for x,y in result])
        self.assertTrue('file_info[status]' in [x for x,y in result])
        self.assertTrue('file_info[fext]' in [x for x,y in result])
        self.assertTrue('file_info[share_name]' in [x for x,y in result])
        self.assertTrue('sample.txt' in [y for x,y in result])
        return

    def test_get_data_odls_vars(self):
        self.createCustomConf(defaults={'odls_vars':'var1=12\nVAR2 = 123'})
        self.createFakeApp()
        client = ODLSHTTPClient(self.app)
        result = client.getData(self.fake_change)
        self.assertTrue(('ODLS_VARS[var1][]', '12') in result)
        self.assertTrue(('ODLS_VARS[var2][]', '123') in result)
        return

    def test_get_data_deleted_file(self):
        client = ODLSHTTPClient(self.app)
        self.fake_change.changetype = DELETED
        result = client.getData(self.fake_change)
        self.assertTrue(('file_info[status]', 'missing') in result)
        return

    def test_respect_no_send_binaries(self):
        self.createCustomConf(defaults={'send_binaries':'no'})
        self.createFakeApp()
        client = ODLSHTTPClient(self.app)
        data = client.getMultipartData(self.fake_change)
        self.assertTrue('binary' not in dict(data[1]).keys())
        self.assertTrue('binary_compressed' not in dict(data[1]).keys())
        return

    def test_respect_send_binaries(self):
        client = ODLSHTTPClient(self.app)
        data = client.getMultipartData(self.fake_change)
        file_keys = [w for w, x, y, z in data[1]]
        self.assertTrue('binary_compressed' in file_keys
                        or 'binary' in file_keys)
        return

    def test_respect_no_send_binaries(self):
        self.createCustomConf(defaults={'send_binaries':'no'})
        self.createFakeApp()
        client = ODLSHTTPClient(self.app)
        data = client.getMultipartData(self.fake_change)
        self.assertTrue('binary' not in dict(data[1]).keys())
        self.assertTrue('binary_compressed' not in dict(data[1]).keys())
        return

class HTTPTest(HTTPTestBase):
    """HTTP tests that require a running server in background.
    """
    
    def setUp(self):
        self.server = SERVER
        self.server.start()
        super(HTTPTest, self).setUp()
        return

    def tearDown(self):
        self.server.stop()
        super(HTTPTest, self).tearDown()
        return

    def restartServer(self, basic_auth=False, digest_auth=False):
        self.server.stop()
        self.server = ODLSServer(
            enable_basic_auth=basic_auth, enable_digest_auth=digest_auth)
        self.server.start()
        return
    
    def test_opener_basic_auth(self):
        self.restartServer(basic_auth=True)
        opener = extended_opener(
            host = self.server_url, username = self.server_username,
            password = self.server_password)
        result = opener.open('http://localhost:8080/')
        self.assertEqual(result.code, 200)
        return
        
    def test_opener_digest_auth(self):
        self.restartServer(digest_auth=True)
        opener = extended_opener(
            host = self.server_url, username = self.server_username,
            password = self.server_password)
        result = opener.open('http://localhost:8080/')
        self.assertEqual(result.code, 200)
        return

    def test_send_change_wo_file(self):
        client = ODLSHTTPClient(self.app)
        response = client.sendChange(self.fake_change)
        self.assertEqual(response.code, 200)

    def test_send_change_plain(self):
        testdoc = os.path.join(self.workdir, 'testdoc.txt')
        open(testdoc, 'wb').write('Hello Test!\n')
        change = FakeChange(testdoc)
        client = ODLSHTTPClient(self.app)
        response = client.sendChange(change)
        response_content = response.read()
        client.opener.close()
        self.assertEqual(response.code, 200)
        self.assertTrue('binary_compressed' in response_content)
        self.assertFalse('Hello Test!' in response_content)

    def test_send_change_plain_uncompressed(self):
        self.createFakeApp(argv=['-c', self.ini_path, '--send-compressed=0'])
        testdoc = os.path.join(self.workdir, 'testdoc.txt')
        open(testdoc, 'wb').write('Hello Test!\n')
        change = FakeChange(testdoc)
        client = ODLSHTTPClient(self.app)
        response = client.sendChange(change)
        response_content = response.read()
        client.opener.close()
        self.assertEqual(response.code, 200)
        self.assertFalse('binary_compressed' in response_content)
        self.assertTrue('binary' in response_content)
        self.assertTrue('Hello Test!' in response_content)

def suite():
    suite = unittest.TestSuite()
    for testcase in             [
                HTTPServerlessTest,
                HTTPTest,
                ]:
        suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(testcase)
            )
    return suite

test_suite = suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')
