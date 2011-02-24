import unittest
import provide.testunit
import provide.dom.buildertest

def suite():
    suites = [
        provide.dom.buildertest.suite(),
    ]
    return unittest.TestSuite(suites)

