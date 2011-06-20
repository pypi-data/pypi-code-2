import unittest
from kforge.testunit import TestCase
import kforge.command.initialisetest
import kforge.command.projecttest
import kforge.command.membertest
import kforge.command.servicetest
import kforge.command.emailpasswordtest
#import kforge.command.projectwithadministratortest
from kforge.exceptions import *

def suite():
    "Return a TestSuite of kforge.command TestCases."
    suites = [
        kforge.command.initialisetest.suite(),
        kforge.command.projecttest.suite(),
        kforge.command.membertest.suite(),
        kforge.command.servicetest.suite(),
#        kforge.command.projectwithadministratortest.suite(),
        kforge.command.emailpasswordtest.suite(),
    ]
    return unittest.TestSuite(suites)

