import unittest2 as unittest

from collective.viewportletmanager.testing import MYPACKAGE_INTEGRATION_TESTING
from collective.viewportletmanager.tests import common
from collective.viewportletmanager.browser.traversal import ViewPortletNamespace
from collective.viewportletmanager.config import VIEW_CATEGORY


class TestViewPortletNamespaceTraversal(unittest.TestCase):

    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_traverse(self):
        dummy_obj = common.DummyObj(uid='1')
        traverser = ViewPortletNamespace(dummy_obj, self.layer['request'])
        manager = traverser.traverse('plone.rightcolumn+nouid:dummy_view', True)

        self.assertEqual(manager.__category__, VIEW_CATEGORY)
        self.assertEqual(manager.__name__, u'nouid:dummy_view')
        self.assertEqual(manager.__manager__, u'plone.rightcolumn')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestViewPortletNamespaceTraversal))
    return suite
