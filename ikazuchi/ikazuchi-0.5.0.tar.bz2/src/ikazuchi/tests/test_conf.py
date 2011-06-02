# -*- coding: utf-8 -*-

import ConfigParser
import os
from nose.tools import *
from os.path import (dirname, join as pathjoin)

# functions for test
from ikazuchi.conf import *

def _assert(expected, actual):
    assert_equal(expected, actual)

class TestExistingConfigFile(object):

    conf_file = pathjoin(dirname(__file__), "data/conf/ikazuchi.conf")

    def test_get_conf(self):
        expected = {"google": {"apikey": "xxx"},
                    "microsoft": {"apikey": "yyy"}}
        conf = get_conf(self.conf_file)
        for sec in SECTIONS:
            for opt in OPTIONS:
                yield _assert, expected[sec][opt], conf.get(sec, opt)


class TestNotExistingConfigFile(object):

    conf_file = pathjoin(dirname(__file__), "data/conf/notexisting.conf")

    def setup(self):
        self._remove_conf()

    def teardown(self):
        self._remove_conf()

    def _remove_conf(self):
        if os.access(self.conf_file, os.R_OK):
            os.remove(self.conf_file)

    def test_get_conf(self):
        expected = {"google": {"apikey": ""},
                    "microsoft": {"apikey": ""}}
        conf = get_conf(self.conf_file)
        for sec in SECTIONS:
            for opt in OPTIONS:
                yield _assert, expected[sec][opt], conf.get(sec, opt)

    def test_create_conf_file(self):
        yield _assert, False, os.access(self.conf_file, os.R_OK)
        create_conf_file(self.conf_file)
        yield _assert, True, os.access(self.conf_file, os.R_OK)

    def test_get_or_set_sections(self):
        conf = ConfigParser.SafeConfigParser()
        get_or_set_sections(conf)
        _assert(SECTIONS, conf.sections())

    def test_get_or_set_options(self):
        conf = ConfigParser.SafeConfigParser()
        expected = {"google": [("apikey", "")],
                    "microsoft": [("apikey", "")]}
        get_or_set_sections(conf)
        for sec in SECTIONS:
            get_or_set_options(conf, sec)
            yield _assert, expected[sec], conf.items(sec)
