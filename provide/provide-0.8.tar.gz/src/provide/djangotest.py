import unittest
import provide.testunit
import provide.django.settingstest

def suite():
    suites = [
        provide.django.settingstest.suite(),
    ]
    return unittest.TestSuite(suites)

