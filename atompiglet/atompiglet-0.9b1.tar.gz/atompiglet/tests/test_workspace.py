#!/usr/bin/env python
# encoding: utf-8
"""
test_workspace.py

Created by Keith Fahlgren on Sun Jan 18 06:59:53 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

from nose.tools import *

from atompiglet import NAMESPACES
from atompiglet.server import Server 
from atompiglet.workspace import Workspace

class TestWorkspace:
    def setup(self):
        self.server = Server(Server.TEST_KURT)

    def test_workspace_oreilly(self):
        """The test server should have an "O'Reilly Media" app:workspace."""
        assert("O'Reilly Media" in self.server.workspaces)

    def test_workspace_title(self):
        """Every Workspace should have a title."""
        for wksp in self.server.workspaces:
            assert(wksp.title)

    def test_oreilly_workspace_collections(self):
        """The test server's "O'Reilly Media" app:workspace should have more than one app:collection"""
        orm_wksp = self.server.workspaces["O'Reilly Media"]
        coll_names = orm_wksp.collections.keys()
        assert(1 < len(coll_names))
    
    def test_oreilly_workspace_collections_for_mimetype(self):
        """Test for the presence of collections with appropriate titles for given mimetypes."""
        orm_wksp = self.server.workspaces["O'Reilly Media"]
        # Images, Web PDFs, Examples, PDFs
        pdf_collections = orm_wksp.collections_for_mimetype(mimetype='application/pdf')
        num_expected_pdf_collections = 4
        assert_equal(num_expected_pdf_collections, len(pdf_collections))
        # Images
        image_collections = orm_wksp.collections_for_mimetype(mimetype='image/bmp')
        num_expected_image_collections = 1
        assert_equal(num_expected_image_collections, len(image_collections))
        assert_equal('Images', image_collections[0].title)
