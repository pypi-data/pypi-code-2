import unittest
import os
import sys
import tempfile

from linkexchange.platform import Platform
from linkexchange.config import file_config
from test_clients import SapeTestServer

class SapeTestServer1(SapeTestServer):
    data = {
        '/': [
            '<a href="url1">xlink1</a>',
            '<a href="url2">xlink2</a>'],
        '/path/1': [
            '<a href="url1">xlink1</a>',
            '<a href="url2">xlink2</a>',
            '<a href="url3">xlink3</a>',
            '<a href="url4">xlink4</a>'],
        '/path/2': [
            'Plain text and <a href="url">link text</a>'],
        '__sape_new_url__': '<!--x12345-->',
        '__sape_delimiter__': '. ',
        }

class SapeTestServer2(SapeTestServer):
    data = {
        '/': [
            '<a href="url1">ylink1</a>'],
        '__sape_new_url__': '<!--y12345-->',
        '__sape_delimiter__': '. ',
        }

class PlatformTest(unittest.TestCase):
    def setUpClass(cls):
        cls.server1 = SapeTestServer1()
        cls.server2 = SapeTestServer2()
        clients = [('sape', [], dict(user='user123456789',
            db_driver=('mem',), server_list=[
		    cls.server1.url.replace('%', '%%')])),
            ('sape', [], dict(user='user123456789',
                db_driver=('mem',), server_list=[
			cls.server2.url.replace('%', '%%')]))]
        cls.platform = Platform(clients=clients)
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        del cls.platform
        del cls.server1
        del cls.server2
    tearDownClass = classmethod(tearDownClass)

    def test_get_raw_links(self):
        lx = self.platform.get_raw_links('http://example.com/')
        self.assertEqual(unicode(lx[0]), '<a href="url1">xlink1</a>')
        self.assertEqual(unicode(lx[1]), '<a href="url2">xlink2</a>')
        self.assertEqual(unicode(lx[2]), '<a href="url1">ylink1</a>')

    def test_get_blocks(self):
        formatters = [
                ('inline', [2], dict(
                    class_='links', class_for_empty='empty', suffix='. ')),
                ('list', [None], dict(id='links')),
                ]
        bx = self.platform.get_blocks(
                'http://example.com/', formatters)
        self.assertEqual(unicode(bx[0]),
                '<div class="links"><a href="url1">xlink1</a>. '
                '<a href="url2">xlink2</a>. </div>')
        self.assertEqual(unicode(bx[1]),
                '<ul id="links"><li><a href="url1">ylink1</a></li></ul>')
        bx = self.platform.get_blocks(
                'http://example.com/notexists', formatters)
        self.assertEqual(unicode(bx[0]),
                '<div class="empty"></div><!--x12345--><!--y12345-->')
        self.assertEqual(unicode(bx[1]),
                '<span id="links"></span>')
        bx = self.platform.get_blocks(
                'http://example.com/path/1', formatters)
        self.assertEqual(unicode(bx[0]),
                '<div class="links"><a href="url1">xlink1</a>.'
                ' <a href="url2">xlink2</a>. </div>')
        self.assertEqual(unicode(bx[1]),
                '<ul id="links"><li><a href="url3">xlink3</a></li>'
                '<li><a href="url4">xlink4</a></li></ul><!--y12345-->')

        formatters = [
                ('inline', [None], dict()),
                ('inline', [None], dict(client=1)),
                ]
        bx = self.platform.get_blocks(
                'http://example.com/', formatters)
        self.assertEqual(unicode(bx[0]),
                '<div><a href="url1">ylink1</a></div>')
        self.assertEqual(unicode(bx[1]),
                '<div><a href="url1">xlink1</a>'
                '<a href="url2">xlink2</a></div>')

class PlatformConfigTest(PlatformTest):
    linkexchange_cfg = """
[client-1]
type = sape
user = user123456789
db_driver.type = mem
server-1 = %(server1)s

[client-2]
type = sape
user = user123456789
db_driver.type = mem
server-1 = %(server2)s
"""
    def setUpClass(cls):
        cls.server1 = SapeTestServer1()
        cls.server2 = SapeTestServer2()

        cfgfd, cls.cfgfn = tempfile.mkstemp()
        os.close(cfgfd)
        open(cls.cfgfn, 'w').write(cls.linkexchange_cfg % {
            'server1': cls.server1.url.replace('%', '%%'),
            'server2': cls.server2.url.replace('%', '%%'),
            })

        vars = {}
        result = file_config(vars, cls.cfgfn)
        assert result == [cls.cfgfn]
        cls.platform = vars['platform']
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        del cls.platform
        del cls.server1
        del cls.server2
        os.unlink(cls.cfgfn)
    tearDownClass = classmethod(tearDownClass)

    def test_lxrefresh(self):
        from linkexchange.commands import lxrefresh
        lx_path = os.path.dirname(os.path.dirname(
            os.path.dirname(lxrefresh.__file__)))
        old_pypath = [x for x in os.getenv('PYTHONPATH',
            '').split(os.pathsep) if x]
        new_pypath = old_pypath[:]
        if not (new_pypath and new_pypath[0] == lx_path):
            new_pypath.insert(0, lx_path)
        os.putenv('PYTHONPATH', os.pathsep.join(new_pypath))
        retcode = os.spawnl(os.P_WAIT, sys.executable, sys.executable,
                lxrefresh.__file__, '-c', self.cfgfn,
                '-r', 'http://example.com')
        self.assertEqual(retcode, 0)
        os.putenv('PYTHONPATH', os.pathsep.join(old_pypath))
