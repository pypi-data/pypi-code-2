import unittest
import quant.testunit
import quant.django.settingstest

def suite():
    suites = [
        quant.django.settingstest.suite(),
    ]
    return unittest.TestSuite(suites)

