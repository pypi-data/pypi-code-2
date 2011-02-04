import unittest
import dm.testunit
import dm.dom.metatest
import dm.dom.accesscontroltest
import dm.dom.persontest
import dm.dom.imagetest
import dm.dom.registrytest
import dm.dom.temporaltest

def suite():
    "Return a TestSuite of dm.db TestCases."
    suites = [
        dm.dom.metatest.suite(),
        dm.dom.accesscontroltest.suite(),
        dm.dom.persontest.suite(),
        dm.dom.imagetest.suite(),
        dm.dom.registrytest.suite(),
        dm.dom.temporaltest.suite(),
    ]
    return unittest.TestSuite(suites)

