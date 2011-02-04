from dm.testunit import *
import dm.plugin.basetest
import dm.plugin.controllertest
import unittest
import os


def suite():
    suites = [
        dm.plugin.basetest.suite(),
        dm.plugin.controllertest.suite(),
    ]
    return unittest.TestSuite(suites)

