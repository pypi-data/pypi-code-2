import unittest
from collective.wowcharacter.tests.base import ExampleTestCase

from Products.CMFCore.utils import getToolByName

from collective.wowcharacter.browser.armory_api import Armory
from collective.wowcharacter.browser.wowcharacter import WoWCharacter

# mock WoWCharacter.make_char
# returns a dictionary similar to the dictionary we would get from the API
# so that this test can be used while offline
def mocked_make_char(self, name, realm, zone):

    d = {}
    d["name"] = name
    d["talents1"] = [58, 0, 13, 'Balance', 'spell_nature_starfall']
    d["talents2"] = [14, 0, 57, 'Restoration', 'spell_nature_healingtouch']
    d["professions"] = [{'key': u'inscription',
                         'max': 450,
                         'name': u'Inscription',
                         'value': 450},
                        {'key': u'jewelcrafting',
                         'max': 450,
                         'name': u'Jewelcrafting',
                         'value': 450}]
    d["items"] = [{'durability': 70,
                   'gems': [41285, 40113, 0],
                   'icon': u'inv_helmet_148',
                   'id': 51149,
                   'maxdurability': 70,
                   'permanentenchant': 3820,
                   'randomPropertiesId': 0,
                   'seed': 0,
                   'slot': 0}]
    d["guild"] = u"Elusive Dreams"
    d["class"] = u"Druid"

    return d

#mocking the function
WoWCharacter.make_char = mocked_make_char

class TestSetup(ExampleTestCase):

    # this function is executet before every testfunction
    # so we have the self.char objekt for further manipulation
    def afterSetUp(self):

        self.setRoles(["Manager"])
        self.portal.invokeFactory("WoW Character", "char_ct")
        self.char_ct = self.portal.char_ct
        self.char = WoWCharacter(self.char_ct, None)

    # unittest for make_char()
    def test_make_char(self):

        raider = self.char.make_char("Kutschurft", "Azshara", "EU")

        self.assertEquals(raider.get("name"), "Kutschurft")

    # unittest for char_professions()
    def test_char_professions(self):

        professions = self.char.char_professions()

        self.assertEquals(professions.get("profession1"), u"Inscription @ 450/450")
        self.assertEquals(professions.get("profession2"), u"Jewelcrafting @ 450/450")

    # unittest for char_equip()
    def test_char_equip(self):

        # because char_equip() is a generator
        # we have to iterate
        for slot in self.char.char_equip():
            item_url = slot.get("item_url")
            icon_url = slot.get("icon_url")
            ench_gems = slot.get("ench_gems")

        self.assertEquals(item_url, "http://www.wowhead.com/item=51149")
        self.assertEquals(icon_url, "http://static.wowhead.com/images/wow/icons/large/inv_helmet_148.jpg")
        self.assertEquals(ench_gems, "ench=3820;gems=41285:40113:0")

    # unittest for char_talents()
    def test_char_talents(self):

        talents = self.char.char_talents()

        self.assertEquals(talents.get("spec1"), "Balance 58/0/13")
        self.assertEquals(talents.get("spec1icon"), "http://eu.wowarmory.com/wow-icons/_images/43x43/spell_nature_starfall.png")
        self.assertEquals(talents.get("spec2"), "Restoration 14/0/57")
        self.assertEquals(talents.get("spec2icon"), "http://eu.wowarmory.com/wow-icons/_images/43x43/spell_nature_healingtouch.png")

    # unittest for char_data()
    def test_char_data(self):

        data = self.char.char_data()

        self.assertEquals(data.get("class"), u"Druid")
        self.assertEquals(data.get("guild"), u"Elusive Dreams")

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))

    return suite
