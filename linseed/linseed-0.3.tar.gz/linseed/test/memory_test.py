import unittest

from linseed import Memory, Swap

class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.m = Memory()
        
    def test_total(self):
        t = self.m.total

    def test_free(self):
        f = self.m.free

    def test_used(self):
        u = self.m.used
        self.assert_(u >= 0 and u <= 100)

class SwapTest(unittest.TestCase):
    def setUp(self):
        self.s = Swap()
        
    def test_total(self):
        t = self.s.total

    def test_free(self):
        f = self.s.free

    def test_used(self):
        u = self.s.used
        self.assert_(u >= 0 and u <= 100)
