import unittest

from linseed import Battery

class Test(unittest.TestCase):
    def test_count(self):
        count = Battery.count()

    def test_constructor(self):
        for bid in range(Battery.count()):
            b = Battery(bid)
            
        for id in [-1, Battery.count()]:
            try:
                Battery(Battery.count())
                self.assert_(False)
            except ValueError:
                pass
            except:
                self.assert_(False)

class InfoTest(unittest.TestCase):
    def test_design_capacity(self):
        for bid in range(Battery.count()):
            x = Battery(bid).info.design_capacity

    def test_last_full_capacity(self):
        for bid in range(Battery.count()):
            x = Battery(bid).info.last_full_capacity

class StateTest(unittest.TestCase):
    def test_charging_state(self):
        for bid in range(Battery.count()):
            x = Battery(bid).state.charging_state

    def test_remaining_capacity(self):
        for bid in range(Battery.count()):
            x = Battery(bid).state.remaining_capacity
