import unittest2 as unittest

from zope.interface import implements

from collective.viewportletmanager.testing import MYPACKAGE_INTEGRATION_TESTING
from collective.viewportletmanager.tests import common
from collective.viewportletmanager.retriever import PortletRetriever
from collective.viewportletmanager.config import VIEW_CATEGORY


class TestPortletRetriever(unittest.TestCase):

    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_getPortlets(self):
        """Here we just check if view parameter is accepted by getPortlets
        method and then passed over to globalPortletCategories of
        PortletCotnext.
        """
        dummy_obj = common.DummyObj(uid='1')
        dummy_view = common.DummyView(dummy_obj, None, name='dummy_view')
        context = common.DummyPortletContext(dummy_obj)
        retriever = PortletRetriever(context, common.DummyStorage({
            VIEW_CATEGORY: {'1:dummy_view': {'dummy_portlet':
            common.DummyPortlet(name='dummy_portlet')}}}, name='dummy_storage'))
        
        portlets = retriever.getPortlets(view=dummy_view)
        self.assertEquals(portlets[0]['name'], 'dummy_portlet')

        # pass no view to retriever on getPortlets call
        portlets = retriever.getPortlets()
        self.assertEquals(len(portlets), 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletRetriever))
    return suite
