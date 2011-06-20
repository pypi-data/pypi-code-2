import dm.test
import unittest

def suite():
    suites = [
        dm.test.suite(),
    ]
    return unittest.TestSuite(suites)

