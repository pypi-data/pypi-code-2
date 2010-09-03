import unittest
from collective.wowcharacter.tests.base import ExampleTestCase

from Products.CMFCore.utils import getToolByName

from collective.wowcharacter.browser.armory_api import Armory

# mock Armory.getCharacter
# returns a dictionary similar to the dictionary we would get from the API
# so that this test can be used while offline
def mocked_getCharacter(self, raiderName, raiderServer, raiderZone):

    d = {}
    d["name"] = raiderName
    d["server"] = raiderServer
    d["zone"] = raiderZone

    return d

# mocking the function
Armory.getCharacter = mocked_getCharacter

class TestSetup(ExampleTestCase):

    # unittest for the realmstatus API
    def test_armory(self):

        raider = Armory().getCharacter("Kutschurft","Azshara","EU")

        name = raider.get("name")
        self.assertEquals(name, "Kutschurft")

        server = raider.get("server")
        self.assertEquals(server, "Azshara")

        zone = raider.get("zone")
        self.assertEquals(zone, "EU")

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))

    return suite
