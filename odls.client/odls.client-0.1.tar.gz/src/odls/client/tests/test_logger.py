##
## test_logger.py
## Login : <uli@pu.smp.net>
## Started on  Sun Sep  5 15:58:16 2010 Uli Fouquet
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

"""Tests for configuration module.
"""
import os
import shutil
import tempfile
import unittest
import logging
from odls.client.logger import init_logger

class FakeConfiguration(object):

    def __init__(self, max_file_size=1024, logname='test.name',
                 do_syslog=False, logfile='indexer.log', loglevel=3):
        self.max_file_size = max_file_size
        self.logname = logname
        self.do_syslog = do_syslog
        self.logfile = logfile
        self.loglevel = loglevel

class LoggerTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.default_conf = FakeConfiguration()
        self.orig_logger = logging.getLogger('test.name')
        return

    def tearDown(self):
        # Remove installed log handlers...
        handlers = self.orig_logger.handlers
        for handler in handlers:
            self.orig_logger.removeHandler(handler)
        shutil.rmtree(self.workdir)
        return

    def test_logger_init_default(self):
        init_logger(self.default_conf)
        logger = logging.getLogger('test.name')
        # The default logger should provide a rotating logfile handler
        self.assertEqual(len(logger.handlers), 1)
        assert isinstance(logger.handlers[0],
                          logging.handlers.RotatingFileHandler)
        return

    def test_logger_init_emergency(self):
        self.default_conf.loglevel = 7
        init_logger(self.default_conf)
        logger = logging.getLogger('test.name')
        self.assertEqual(logger.level, logging.FATAL)
        return

    def test_logger_init_syslog(self):
        self.default_conf.do_syslog = True
        init_logger(self.default_conf)
        logger = logging.getLogger('test.name')
        self.assertEqual(len(logger.handlers), 2)
        assert isinstance(logger.handlers[1],
                          logging.handlers.SysLogHandler)
        return
        

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        LoggerTestCase)
    return suite

test_suite = suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')

