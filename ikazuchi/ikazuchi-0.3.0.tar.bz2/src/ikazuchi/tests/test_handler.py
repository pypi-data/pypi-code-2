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

    class Option(object):
        sentence = ""
        encoding = ["utf-8", "utf-8"]
        quiet = False
        detect = False

    def setup(self):
        sys.stdout = StringIO()
        self.opts = TestSingleSentenceHandler.Option()

    def _dummy_translate(self, sentence):
        yield "", sentence

    def test_with_quiet_option(self):
        self.opts.quiet = True
        h = SingleSentenceHandler(self.opts)
        h._call_method(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal("translate():             ", first_line)

    def test_detect_with_quiet_option(self):
        self.opts.quiet = True
        self.opts.detect = True
        h = SingleSentenceHandler(self.opts)
        h._call_method(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal("detect():                ", first_line)

    def test_without_quiet_option(self):
        h = SingleSentenceHandler(self.opts)
        h._call_method(self._dummy_translate)
        first_line = sys.stdout.getvalue().split('\n')[0]
        assert_equal("sentence:                ", first_line)
