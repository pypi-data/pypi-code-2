import unittest
from collective.wowcharacter.tests.base import ExampleTestCase

from Products.CMFCore.utils import getToolByName

from collective.wowcharacter.portlets.realmstatus_api import Realmstatus

# mock Realmstatus.get_realm_status
# returns outup similar to what we would get from the API
# so that this test can be used while offline
def mocked_get_realm_status(self, name):

    if name == "Azshara":
        return "Realm Up"
    else:
        return "Realm not found"

# mock Realmstatus.get_realm_status
# returns outup similar to what we would get from the API
# so that this test can be used while offline
def mocked_get_realm_type(self, name):

    if name == "Azshara":
        return "PvP"
    else:
        return "Realm not found"

# mocking the functions
Realmstatus.get_realm_status = mocked_get_realm_status
Realmstatus.get_realm_type = mocked_get_realm_type

class TestSetup(ExampleTestCase):

    # unittest for the armory API
    def test_realmstatus(self):

        realmstatus = Realmstatus()

        status = realmstatus.get_realm_status("Azshara")
        type = realmstatus.get_realm_type("Azshara")

        self.assertEquals(status, "Realm Up")
        self.assertEquals(type, "PvP")

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))

    return suite
