import sys

from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy import TenpyConfig


class TenpyConfigTest(TestCase):

    def setUp(self):
        self.test_config = TenpyConfig()

    def test_getitem(self):
        self.assertListEqual(self.test_config["template_extensions"], [".html"])
        with self.assertRaises(KeyError):
            self.test_config["key_nothing"]

    def test_setitem(self):
        self.test_config["template_extensions"] = [".xml"]
        self.assertListEqual(self.test_config["template_extensions"], [".xml"])
        with self.assertRaises(KeyError):
            self.test_config["key_nothing"] = "nothing"

    def test_setattr(self):
        self.test_config.template_extensions = [".xml"]
        self.assertListEqual(self.test_config.template_extensions, [".xml"])
        with self.assertRaises(AttributeError):
            self.test_config.attr_nothing = "nothing"


def test_main():
    support.run_unittest(TenpyConfigTest)

if __name__ == "__main__":
    test_main()
