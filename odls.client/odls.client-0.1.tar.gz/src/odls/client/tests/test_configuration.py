##
## test_configuration.py
## Login : <uli@pu.smp.net>
## Started on  Thu Dec  3 10:41:58 2009 Uli Fouquet
## $Id$
## 
## Copyright (C) 2009 Uli Fouquet
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
"""Tests for configuration module.
"""
import os
import shutil
import tempfile
import types
import unittest
from odls.client.configuration import ODLSConfiguration

DEFAULTS = dict(
    odls_vars="",
    server_url="",
    timeout="3",
    odls_username="test",
    odls_password="test",
    http_username_prefix="# ",
    http_username="",
    http_pw_prefix="# ",
    http_pw="",
    proxy_server_prefix="# ",
    proxy_server="localhost:7777",
    proxy_user_prefix="# ",
    proxy_user="bar",
    proxy_pw_prefix="# ",
    proxy_pw="secret",
    watch_files="",
    watch_files_prefix="",
    watch_folders="",
    watch_blacklist="""*~
  ~*""",
    watch_updatetime="300",
    watch_old_discard="900",
    watch_ignore_odls_failure="yes",
    watch_ignore_odls_unreadable="yes",
    send_binaries="yes",
    send_keywords="yes",
    send_fulltext="no",
    send_compressed="yes",
    output_encoding="ISO-8859-15",
    do_syslog="no",
    logfile_prefix="# ",
    logfile="indexer.log",
    max_file_size="1048576",
    logserver_prefix="# ",
    logserver="logserv.company.net",
    loglevel="WARN",
    dbfile='indexer.db',
    )

def create_custom_conf(path, defaults=dict()):
    """Create a custom config file in `path`.

    The values set in the config file are the defaults above, updated
    with the `defaults` passed in.
    """
    user_defaults = defaults
    defaults = DEFAULTS.copy()
    defaults.update(user_defaults)
    template = open(
        os.path.join(os.path.dirname(__file__), 'indexer_ini.template'),
        'rb'
        ).read()
    template = template % defaults
    open(path, 'wb').write(template)
    return

def create_default_ini():
    """Create the default ini file.
    """
    default_ini = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'default.ini'
        )
    create_custom_conf(default_ini)
    return

class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        create_default_ini()
        default_conf = os.path.join(os.path.dirname(__file__),
                                    '..', 'default.ini')
        self.workdir = tempfile.mkdtemp()
        self.conf1 = os.path.join(self.workdir, 'conf1')
        self.conf2 = os.path.join(self.workdir, 'conf2')
        self.customconf = os.path.join(self.workdir, 'custom.conf')
        self.fillCustomConf(defaults=dict(
            watch_file='sample',
            watch_folders='"sampledir"'
            ))
        shutil.copy(default_conf, self.conf1)
        shutil.copy(self.customconf, self.conf2)
        return

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def fillCustomConf(self, defaults=dict()):
        create_custom_conf(path=self.customconf, defaults=defaults)
        return
        
    def test_option_quiet(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.quiet
        config1 = ODLSConfiguration(argv=["-c", self.conf1])
        option1 = config1.options.quiet
        config2 = ODLSConfiguration(argv=["-q"])
        option2 = config2.options.quiet
        self.assertTrue(isinstance(option0, types.BooleanType))
        self.assertFalse(option0)
        self.assertFalse(option1)
        self.assertTrue(option2)
        return

    def test_option_watch_file(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.watch_files
        self.fillCustomConf(dict(watch_files='sample'))
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.watch_files
        self.fillCustomConf(dict(
                watch_files="sample" + os.linesep +" otherfile"))
        config2 = ODLSConfiguration(argv=["-c", self.customconf])
        option2 = config2.options.watch_files
        self.fillCustomConf(dict(watch_files_prefix='# '))
        config3 = ODLSConfiguration(argv=["-c", self.customconf])
        option3 = config3.options.watch_files
        self.assertTrue(isinstance(option0, types.ListType))
        self.assertEqual(option0, [])
        self.assertEqual(option1, ['sample'])
        self.assertEqual(option2, ['sample', 'otherfile'])
        self.assertEqual(option3, [])
        return

    def test_option_logname(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.logname
        config1 = ODLSConfiguration(argv=["--name", "foo.bar"])
        option1 = config1.options.logname
        config2 = ODLSConfiguration(argv=["-n", "bar.baz"])
        option2 = config2.options.logname
        self.assertEqual(option0, 'odls.client')
        self.assertEqual(option1, 'foo.bar')
        self.assertEqual(option2, 'bar.baz')
        return

    def test_option_proxy_server(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.proxy_server
        assert option0 is None

        self.fillCustomConf(dict(proxy_server_prefix='',
                                 proxy_server=' \n ',))
        config = ODLSConfiguration(argv=["-c", self.customconf])
        option = config.options.proxy_server
        assert option is ""

        self.fillCustomConf(dict(proxy_server_prefix='',
                                 proxy_server='localhost:7777',))
        config = ODLSConfiguration(argv=["-c", self.customconf])
        option = config.options.proxy_server
        assert option == "localhost:7777"

    def test_option_odls_username(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.odls_username
        
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.odls_username

        self.fillCustomConf(dict(odls_username='foo',
                                 odls_password='bar',))
        config2 = ODLSConfiguration(argv=["-c", self.customconf])
        option2 = config2.options.odls_username

        self.assertEqual(option0, 'test')
        self.assertEqual(option1, 'test')
        self.assertEqual(option2, 'foo')
        return

    def test_option_http_username(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.http_username
        
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.http_username

        self.fillCustomConf(dict(http_username='test',
                                 http_username_prefix='',))
        config2 = ODLSConfiguration(argv=["-c", self.customconf])
        option2 = config2.options.http_username

        self.assertEqual(option0, None)
        self.assertEqual(option1, None)
        self.assertEqual(option2, 'test')
        return

    def test_option_logfile(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.loglevel
        self.assertEqual(option0, 3)

        self.fillCustomConf(dict(loglevel='EMERG'))
        config0 = ODLSConfiguration(argv=["-c", self.customconf])
        option0 = config0.options.loglevel
        self.assertEqual(option0, 7)

        self.fillCustomConf(dict(loglevel='ALERT'))
        args = ["-c", self.customconf]
        self.assertRaises(ValueError, ODLSConfiguration, argv=args)

    def test_option_send_binaries(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.send_binaries
        config1 = ODLSConfiguration(argv=["--send-binaries=1", self.conf1])
        option1 = config1.options.send_binaries
        config2 = ODLSConfiguration(argv=["--send-binaries=0", self.conf1])
        option2 = config2.options.send_binaries
        self.assertTrue(isinstance(option0, types.BooleanType))
        self.assertEqual(option0, True)
        self.assertEqual(option1, True)
        self.assertEqual(option2, False)
        return

    def test_option_send_compressed(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.send_compressed
        config1 = ODLSConfiguration(argv=["--send-compressed=1", self.conf1])
        option1 = config1.options.send_compressed
        config2 = ODLSConfiguration(argv=["--send-compressed=0", self.conf1])
        option2 = config2.options.send_compressed
        self.assertTrue(isinstance(option0, types.BooleanType))
        self.assertEqual(option0, True)
        self.assertEqual(option1, True)
        self.assertEqual(option2, False)
        return

    def test_option_nohttpout(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.nohttpout
        config1 = ODLSConfiguration(argv=["--nohttpout"])
        option1 = config1.options.nohttpout
        config2 = ODLSConfiguration(argv=["-2"])
        option2 = config2.options.nohttpout

        self.assertEqual(option0, False)
        self.assertEqual(option1, True)
        self.assertEqual(option2, True)
        return

    def test_option_dbfile(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.dbfile

        self.fillCustomConf(dict(dbfile='anotherpath.db',))
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.dbfile

        config2 = ODLSConfiguration(argv=["--dbfile=someotherpath.db"])
        option2 = config2.options.dbfile

        config3 = ODLSConfiguration(argv=["-c", self.customconf,
                                          "--dbfile=thirdpath.db"])
        option3 = config3.options.dbfile

        self.assertEqual(option0, 'indexer.db')
        self.assertEqual(option1, 'anotherpath.db')
        self.assertEqual(option2, 'someotherpath.db')
        self.assertEqual(option3, 'thirdpath.db')
        return

    def test_option_ignore_odls_failure(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.watch_ignore_odls_failure

        self.fillCustomConf(dict(
                watch_ignore_odls_failure='no',))
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.watch_ignore_odls_failure

        self.fillCustomConf(dict(
                watch_ignore_odls_failure='yes',))
        config2 = ODLSConfiguration(argv=["-c", self.customconf])
        option2 = config2.options.watch_ignore_odls_failure

        self.assertEqual(option0, True)
        self.assertEqual(option1, False)
        self.assertEqual(option2, True)
        return

    def test_configfile_odlsvars(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.odls_vars

        self.fillCustomConf(
            dict(odls_vars="""VAR1=12"""))
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.odls_vars

        self.fillCustomConf(
            dict(odls_vars="VAR1=12\nvAr2='Hello', 'foo'"))
        config2 = ODLSConfiguration(argv=["-c", self.customconf])
        option2 = config2.options.odls_vars

        self.assertEqual(option0, {})
        self.assertEqual(option1, {'var1':'12'})
        self.assertEqual(option2, {'var1': '12', 'var2': "'Hello', 'foo'"})
        return

    def test_configfile_watchupdatetime(self):
        config0 = ODLSConfiguration(argv=[])
        option0 = config0.options.watch_updatetime

        self.fillCustomConf(
            dict(watch_updatetime="""100"""))
        config1 = ODLSConfiguration(argv=["-c", self.customconf])
        option1 = config1.options.watch_updatetime
        self.assertEqual(option0, 300L)
        self.assertEqual(option1, 100)

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        ConfigurationTestCase)
    return suite

test_suite = suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')

