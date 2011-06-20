import unittest
import kforge.test.developer

def suite():
    suites = [
        kforge.test.developer.suite(),
    ]
    return unittest.TestSuite(suites)

