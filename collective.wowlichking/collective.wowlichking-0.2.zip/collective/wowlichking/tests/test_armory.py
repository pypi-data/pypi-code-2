import unittest
from inquant.wow.tests.base import ExampleTestCase
from inquant.wow.browser.armory import Armory

from Products.CMFCore.utils import getToolByName

# mock Char.make_char

from inquant.wow.browser.char import Char

def mocked_make_char(self, name, realm, zone):
    """ uses the armory.py api """
    logger.info("make_char::name=%s, realm=%s, zone=%s" % (name, realm, zone))

    try:
        return armory.getCharacter(raiderName=name,raiderServer=realm,raiderZone=zone)
    except SocketError:
        return dict()

Char.make_char = mocked_make_char

class TestSetup(ExampleTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')

    def beforeTearDown(self):

    def test_portal_title(self):
        self.assertEquals("Plone site", self.portal.getProperty('title'))

    def test_able_to_add_document(self):
        new_id = self.folder.invokeFactory('Document', 'my-page')
        self.assertEquals('my-page', new_id)

    def test_armory(self):
        armory = Armory()
        raider = armory.getCharacter("Kutschurft","Azshara","EU")
        name = raider.get("name")
        self.assertEquals(name, "Kutschurft")

    def test_char(self):
        self.setRoles(['Manager',])
        self.portal.invokeFactory("char", "char_ct")
        char_ct = self.portal.char_ct
        mychar = Char(char_ct, None)
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
