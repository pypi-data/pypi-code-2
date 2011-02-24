import unittest
import provide.plugin.basetest
import provide.plugin.exampletest
import provide.plugin.scanbookertest
import provide.plugin.kforgetest
import provide.plugin.eternitytest
import provide.plugin.desiretest
import provide.plugin.apachetest

def suite():
    suites = [
        provide.plugin.basetest.suite(),
        provide.plugin.exampletest.suite(),
#        provide.plugin.scanbookertest.suite(),
#        provide.plugin.kforgetest.suite(),
#        provide.plugin.eternitytest.suite(),
        provide.plugin.desiretest.suite(),
        provide.plugin.apachetest.suite(),
    ]
    return unittest.TestSuite(suites)

