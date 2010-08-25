#!/usr/bin/env python
# encoding: utf-8
"""
test_server.py

Created by Keith Fahlgren on Sat Jan 17 14:14:36 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import re

from nose.tools import *

from atompiglet import NAMESPACES
from atompiglet.server import Server 
from atompiglet.entry import Entry
from atompiglet.errors import NotFoundError, ServerError, AtomPigletError

class TestServer:
    def setup(self):
        self.server = Server(Server.TEST_KURT)

    def test_server_sanity(self):
        """An interaction with an existing AtomPub server should be creatable."""
        server = Server(Server.TEST_KURT)
        assert(server)

    def test_server_insanity(self):
        """An interaction with a non-existent server should not be createable."""
        assert_raises(ServerError, Server, 'not a server')

    def test_server_non_atompub(self):
        """An interaction with a non-AtomPub server should not be createable."""
        assert_raises(ServerError, Server, 'http://google.com')

    def test_server_non_responsive(self):
        """An interaction with an unresponsive server should not be createable."""
        trailing = re.compile('\/[^\/]+$')
        wrong_url = trailing.sub('', Server.TEST_KURT)
        assert_raises(ServerError, Server, wrong_url)



    def test_server_root(self):
        """The test server's service endpoint should have a app:service document at its root."""
        service_doc = self.server.service_doc()
        root = service_doc.getroot()
        assert_equal('{%s}service' % NAMESPACES['app'], root.tag)

    def test_server_workspaces(self):
        """The test server should have more than one app:workspaces."""
        wksp_names = self.server.workspaces.keys()
        assert(len(wksp_names) > 1)


