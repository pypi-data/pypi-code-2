# -*- coding: utf-8 -*-

import tempfile
from nose.tools import *

# functions for test
from ikazuchi.izuchi.handler import *


class TestPOFileHandler(object):

    def setup(self):
        def make_po_file(path):
            f = tempfile.NamedTemporaryFile(dir=path)
            f.write('msgid "forest"\nmsgstr ""\nmsgid "book"\nmsgstr "hon"')
            f.flush()
            return f
        self.po_file = make_po_file(tempfile.tempdir)

    def teardown(self):
        self.po_file.close()

    def test_select_translation(self):
        data = [
            (["ref", "", "y"], "ref"),
            (["ref", "cur", "y"], "ref"),
            (["ref", "cur", ""], "cur"),
            (["ref", "", ""], ""),
            (["ref", "cur", "ent"], "ent"),
            (["ref", "", "ent"], "ent"),
        ]
        h = POFileHandler(self.po_file.name)
        for d in data:
            assert_equals(d[1], h._select_translation(*d[0]))
