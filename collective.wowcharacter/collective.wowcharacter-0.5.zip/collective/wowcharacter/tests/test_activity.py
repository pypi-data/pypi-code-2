import unittest
from collective.wowcharacter.tests.base import ExampleTestCase

from Products.CMFCore.utils import getToolByName

from collective.wowcharacter.browser.activity_api import Activity

# mock Realmstatus.get_realm_status
# returns output similar to what we would get from the API
# so that this test can be used while offline
def mocked_get_activity(self, name, realm, zone, language, count):

    activity = [u'Earned the achievement [Neck-Deep in Vile (10 player)].',
                u'Has now completed [Victories over the Lich King (Icecrown 10 player)] 4 times.',
                u'Has now completed [Sindragosa kills (Heroic Icecrown 10 player)] 2 times.',
                u'Has now completed [Valithria Dreamwalker rescues (Heroic Icecrown 10 player)] 4 times.',
                u"Has now completed [Blood Queen Lana'thel kills (Heroic Icecrown 10 player)] 6 times."]

    return activity

# mocking the functions
Activity.get_activity = mocked_get_activity

class TestSetup(ExampleTestCase):

    # unittest for the activity API
    def test_activity(self):

        activity = Activity()

        activities = activity.get_activity("Kutschurft", "Azshara", "EU", "en", 6)
        test_activities = [u'Earned the achievement [Neck-Deep in Vile (10 player)].',
                           u'Has now completed [Victories over the Lich King (Icecrown 10 player)] 4 times.',
                           u'Has now completed [Sindragosa kills (Heroic Icecrown 10 player)] 2 times.',
                           u'Has now completed [Valithria Dreamwalker rescues (Heroic Icecrown 10 player)] 4 times.',
                           u"Has now completed [Blood Queen Lana'thel kills (Heroic Icecrown 10 player)] 6 times."]

        self.assertEquals(activities, test_activities)

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))

    return suite
