#!/usr/bin/python

import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from nfg.mt940.parser import MT940

testfile = '/home/paul/Documents/bank/ABNALL/MT940091026101000.STA'
TESTDATA = None

class testParser(unittest.TestCase):

    def setUp(self):
        global TESTDATA
        if TESTDATA: return
        if not os.path.isfile(testfile):
            raise Exception, "Please specify testfile with MT940 data"
        TESTDATA = open(testfile).read()

    def test_parser(self):
        print MT940(TESTDATA)

if __name__ == '__main__':
    unittest.main()
