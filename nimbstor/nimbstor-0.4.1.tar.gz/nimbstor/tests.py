import unittest
import doctest
import nimbstor.stor

test_all = unittest.TestSuite()
test_all.addTest(doctest.DocTestSuite(nimbstor.stor))
