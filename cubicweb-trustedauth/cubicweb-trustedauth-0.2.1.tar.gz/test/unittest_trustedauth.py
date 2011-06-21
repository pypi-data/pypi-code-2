# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.

"""unit tests for cubicweb.web.application"""

import base64, Cookie
import os
import sys
import logging
import tempfile

from logilab.common.testlib import TestCase, unittest_main
from logilab.common.decorators import clear_cache, classproperty

from cubicweb import AuthenticationError, Unauthorized
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools.fake import FakeRequest
from cubicweb.web import LogOut, Redirect, INTERNAL_FIELD_VALUE
from cubicweb.web.views.basecontrollers import ViewController

CONFIG = u'''trustedauth-secret-key-file=%s'''
secretfile = None

def setUpModule():
    global secretfile
    config = TrustAuthTC.config
    home = config.apphome
    print home

class TrustAuthTC(CubicWebTC):

    ## def setup_database(self):
    ##     for log in 'cubicweb', 'cubicweb.cubes', 'cubicweb.twisted':
    ##         logger = logging.getLogger(log)
    ##         logger.handlers = [logging.StreamHandler(sys.stdout)]
    ##         logger.setLevel(logging.DEBUG)

    def test_login(self):
        req, origsession = self.init_authentication('http')
        req._headers['x-remote-user'] = 'admin'
        self.assertAuthSuccess(req, origsession)
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEqual(len(self.open_sessions), 0)

    def test_failed_login(self):
        req, origsession = self.init_authentication('http')
        req._headers['x-remote-user'] = 'toto'
        self.assertAuthFailure(req)
        req._headers['x-remote-user'] = 'admin'
        self.assertAuthSuccess(req, origsession)
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEqual(len(self.open_sessions), 0)
