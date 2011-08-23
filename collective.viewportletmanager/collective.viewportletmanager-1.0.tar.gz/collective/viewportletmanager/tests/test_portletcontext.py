import unittest2 as unittest

from collective.viewportletmanager.testing import MYPACKAGE_INTEGRATION_TESTING
from collective.viewportletmanager.tests import common
from collective.viewportletmanager.portletcontext import ContentContext
from collective.viewportletmanager.config import VIEW_CATEGORY


class TestPortletContext(unittest.TestCase):

    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_getViewKey(self):
        dummy_obj = common.DummyObj(uid='1')
        dummy_view = common.DummyView(dummy_obj, None, name='dummy_view')
        context = ContentContext(dummy_obj)
        
        # check key with view=None
        self.assertEqual(context._getViewKey(None), None)
        
        # check key with both view and context object provided
        self.assertEqual(context._getViewKey(dummy_view), '1:dummy_view')
        
        # check key with object that doesn't provide UID method
        self.assertEqual(ContentContext(common.NoUIDDummyObj())._getViewKey(
            dummy_view), 'nouid:dummy_view')

    def test_globalPortletCategories(self):
        dummy_obj = common.DummyObj(uid='1')
        dummy_view = common.DummyView(dummy_obj, None, name='dummy_view')
        context = ContentContext(dummy_obj)
        
        # view category to be ommited from resulting tuple for view=None
        cats = context.globalPortletCategories(view=None)
        self.failIf(len([c for c in cats if c[0] == VIEW_CATEGORY]) > 0)
        
        # pass view and see if we got view category in resultin tuple
        cats = context.globalPortletCategories(view=dummy_view)
        self.failIf(len([c for c in cats if c[0] == VIEW_CATEGORY]) == 0)
        self.assertEqual(cats[-1][1], '1:dummy_view')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletContext))
    return suite
