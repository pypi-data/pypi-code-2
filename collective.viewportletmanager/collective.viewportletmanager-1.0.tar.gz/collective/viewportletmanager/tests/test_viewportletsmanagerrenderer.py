import unittest2 as unittest

from zope.interface import alsoProvides
from zope.component import provideAdapter

from plone.portlets.manager import PortletManager
from plone.portlets.interfaces import IPortletRenderer

from collective.viewportletmanager.testing import MYPACKAGE_INTEGRATION_TESTING
from collective.viewportletmanager.tests import common
from collective.viewportletmanager.config import VIEW_CATEGORY
from collective.viewportletmanager.manager import ViewPortletsManagerRenderer
from collective.viewportletmanager.interfaces import IPortletsAwareView


class TestViewPortletsManagerRenderer(unittest.TestCase):

    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.dummy_obj = common.DummyObj(uid='1')
        self.dummy_view = common.DummyView(self.dummy_obj, None,
            name='dummy_view')
        alsoProvides(self.dummy_view, IPortletsAwareView)
        self.manager = PortletManager()
        self.manager[VIEW_CATEGORY] = {'1:dummy_view': {'dummy_portlet':
            common.DummyPortlet(name='dummy_portlet')}}
        # register portlet renderer for DummyPortlet
        provideAdapter(common.DummyPortletRenderer, provides=IPortletRenderer,
            name='')

    def test_lazyLoadPortlets(self):
        """Check if renderer passes view argument to retriever"""
        renderer = ViewPortletsManagerRenderer(self.dummy_obj,
            self.layer['request'], self.dummy_view, self.manager)
        portlets = renderer._lazyLoadPortlets(self.manager)
        self.assertEqual(len(portlets), 1)
        self.assertEqual(portlets[0]['name'], 'dummy_portlet')
    
    def test_lazyLoadPortlets_noview(self):
        # now check renderer w/o view argument
        renderer = ViewPortletsManagerRenderer(self.dummy_obj,
            self.layer['request'], None, self.manager)
        portlets = renderer._lazyLoadPortlets(self.manager)
        self.assertEqual(len(portlets), 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestViewPortletsManagerRenderer))
    return suite
