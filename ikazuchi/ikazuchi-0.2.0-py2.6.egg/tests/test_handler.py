# -*- coding: utf-8 -*-

import sys
import tempfile
from nose.tools import *
from StringIO import StringIO

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
        h = POFileHandler(self.po_file.name, ["utf-8", "utf-8"])
        for d in data:
            assert_equals(d[1], h._select_translation(*d[0]))


class TestSingleSentenceHandler(object):

    def setup(self):
        sys.stdout = StringIO()

    def _dummy_translate(self, sentence):
        yield "", sentence

    def test_with_quiet_option(self):
        h = SingleSentenceHandler("", ["utf-8", "utf-8"], True)
        h._translate(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal(u'translated():\t', first_line)

    def test_without_quiet_option(self):
        h = SingleSentenceHandler("", ["utf-8", "utf-8"], False)
        h._translate(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal(u'sentence:\t\t', first_line)
