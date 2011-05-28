# -*- coding: utf-8 -*-
import unittest, os
from pyhole.yamled import PyHoleYamled
    

class TestPyHoleConnection(unittest.TestCase):
    def setUp(self):
        self.path = os.path.dirname(os.getcwd() + '/' + __file__)
        self.pyhole = PyHoleYamled('file://' + self.path, force_slash=False)

    def test_get(self):
        self.assertEqual(self.pyhole.yaml.get(), [1,2,3])
    def test_post(self):
        self.assertEqual(self.pyhole.yaml.get(), [1,2,3])
    

        

if __name__ == '__main__':
    unittest.main()