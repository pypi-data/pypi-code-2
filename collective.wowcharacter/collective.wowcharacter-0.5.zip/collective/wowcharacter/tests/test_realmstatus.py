import unittest
from collective.wowcharacter.tests.base import ExampleTestCase

from Products.CMFCore.utils import getToolByName

from collective.wowcharacter.portlets.realmstatus_api import Realmstatus

# mock Realmstatus.get_realm_status
# returns output similar to what we would get from the API
# so that this test can be used while offline
def mocked_get_realm_status(self, name):

    realmstatus = {}

    if name == "Azshara":
        realmstatus[name] = "Realm Up"

    return realmstatus

# mock Realmstatus.get_realm_type
# returns output similar to what we would get from the API
# so that this test can be used while offline
def mocked_get_realm_type(self, name):

    realmtype = {}

    if name == "Azshara":
        realmtype[name] = "PvP"

    return realmtype

# mocking the functions
Realmstatus.get_realm_status = mocked_get_realm_status
Realmstatus.get_realm_type = mocked_get_realm_type

class TestSetup(ExampleTestCase):

    # unittest for the realmstatus API
    def test_realmstatus(self):

        realmstatus = Realmstatus()

        status = realmstatus.get_realm_status("Azshara")["Azshara"]
        type = realmstatus.get_realm_type("Azshara")["Azshara"]

        self.assertEquals(status, "Realm Up")
        self.assertEquals(type, "PvP")

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))

    return suite
