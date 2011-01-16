import unittest

from linseed import Snapshot

class Test(unittest.TestCase):
    def test_constructor(self):
        s = Snapshot()

    def test_battery(self):
        s = Snapshot(battery=True)
        for i in range(len(s.battery)):
            b = s.battery[i]

        s = Snapshot(battery=False)
        self.assert_(len(s.battery) == 0)

    def test_cpu(self):
        s = Snapshot(cpu=True)
        for i in range(len(s.cpu)):
            c = s.cpu[i]

        s = Snapshot(cpu=False)
        self.assert_(len(s.cpu) == 0)

    def test_memory(self):
        s = Snapshot(memory=True)
        self.assert_(s.memory is not None)
        self.assert_(s.swap is not None)

        s = Snapshot(memory=False)
        self.assert_(s.memory is None)
        self.assert_(s.swap is None)

    def test_wicd(self):
        s = Snapshot(wicd=True)
        self.assert_(s.wicd is not None)

        s = Snapshot(wicd=False)
        self.assert_(s.wicd is None)
