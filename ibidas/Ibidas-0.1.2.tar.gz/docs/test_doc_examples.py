from ibidas import *

class TestTutorial(unittest.TestCase):
    def test_scalar(self):
        r = rep(3)
        self.assertTrue(((r + 3) * r) == 18)

    
