import unittest

from linseed import WICD

class Test(unittest.TestCase):
    def setUp(self):
        self.wicd = WICD()

    def test_is_wireless(self):
        self.wicd.is_wireless

    def test_essid(self):
        if self.wicd.is_wireless:
            self.wicd.essid

    def test_quality(self):
        if self.wicd.is_wireless:
            self.wicd.quality

    def test_is_wired(self):
        self.wicd.is_wired

    def test_str(self):
        str(self.wicd)
