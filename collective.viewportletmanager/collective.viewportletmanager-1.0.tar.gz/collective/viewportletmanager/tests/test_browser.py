import unittest2 as unittest

from zope.interface import alsoProvides
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager, \
    ILocalPortletAssignmentManager

from plone.portlets.manager import PortletManager

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout, setRoles

from collective.viewportletmanager.testing import MYPACKAGE_INTEGRATION_TESTING
from collective.viewportletmanager.tests import common
from collective.viewportletmanager.browser.manage import \
    ManageContextualPortlets, ManageViewPortlets, ManageViewPortletsLinkViewlet
from collective.viewportletmanager.browser.editmanager import \
    ViewEditPortletManagerRenderer
from collective.viewportletmanager.config import VIEW_CATEGORY


class TestManageContextualPortlets(unittest.TestCase):
    """Tests Portlet Manager Renderer that renders portlets in edit mode."""

    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_set_blacklist_status(self):
        # create fake content object and wrap it up into portal object
        # to inherit security settings
        dummy_obj = common.DummyObj(uid='1').__of__(self.portal)
        alsoProvides(dummy_obj, ILocalPortletAssignable)
        view = ManageContextualPortlets(dummy_obj, self.layer['request'])
        
        # make test user a manager
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        result = view.set_blacklist_status('plone.rightcolumn', 1, 1, 1, 1)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        
        self.assertEqual(result, '')
        self.failUnless(self.layer['request'].response.getHeader('Location'
            ).endswith('/@@manage-portlets'))

        # the only thing we really need to check here is whether blacklist
        # status for 'view' category was set properly
        portletManager = getUtility(IPortletManager, name='plone.rightcolumn')
        assignable = getMultiAdapter((dummy_obj, portletManager,),
            ILocalPortletAssignmentManager)
        self.assertEqual(assignable.getBlacklistStatus(VIEW_CATEGORY), True)

class TestManageViewPortlets(unittest.TestCase):
    """Tests manage-view-portlets view methods"""
    
    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.dummy_obj = common.DummyObj(id='dummy_obj',
            uid='1').__of__(self.portal)
        self.view = ManageViewPortlets(self.dummy_obj, self.request)

    def test_disable_borders(self):
        self.assertEqual(self.request.get('disable_border'), True)

    def test_category(self):
        self.assertEqual(self.view.category, VIEW_CATEGORY)
    
    def test_key(self):
        self.request.set('key', 'test key')
        self.assertEqual(self.view.key, 'test key')
    
    def test_getAssignmentMappingUrl(self):
        self.request.set('key', '1:dummy_view')
        manager = PortletManager()
        manager.__name__ = 'dummy_manager'
        self.assertEqual(self.view.getAssignmentMappingUrl(manager),
            '%s/dummy_obj/++viewportlets++dummy_manager+1:dummy_view' %
            self.portal.absolute_url())

    def test_getAssignmentsForManager(self):
        self.request.set('key', '1:dummy_view')
        manager = PortletManager()
        manager.__name__ = 'plone.rightcolumn'
        
        assignments = self.view.getAssignmentsForManager(manager)
        self.assertEqual(assignments, [])
        manager = getUtility(IPortletManager, name='plone.rightcolumn')
        self.assertEqual(manager[VIEW_CATEGORY]['1:dummy_view'].__category__,
            VIEW_CATEGORY)

    def test_view_name(self):
        self.request.set('key', '1:dummy_view')
        self.assertEqual(self.view.view_name, 'dummy_view')
        
        self.request.set('key', '1:cool_view:dummy_view')
        self.assertEqual(self.view.view_name, 'cool_view')
        
        self.request.set('key', '1')
        try:
            view_name = self.view.view_name
        except IndexError, e:
            pass
        else:
            self.fail('view_name attribute should raise IndexError.')

class TestManageViewPortletsLinkViewlet(unittest.TestCase):
    """Tests Manage View Portlets link viewlet."""
    
    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.dummy_obj = common.DummyObj(id='dummy_obj',
            uid='1').__of__(self.portal)
        self.view = common.DummyView(self.dummy_obj, self.request,
            name='dummy_view')

    def test_update(self):
        viewlet = ManageViewPortletsLinkViewlet(self.dummy_obj, self.request,
            self.view, None)
        viewlet.update()
        
        self.assertEqual(viewlet.available, True)
        self.assertEqual(viewlet.url,
            '%s/dummy_obj/@@manage-view-portlets?key=1:dummy_view' %
            self.portal.absolute_url())

class TestViewEditPortletManagerRenderer(unittest.TestCase):
    """Tests inherited portlets on manage-portlets view."""
    
    layer = MYPACKAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_inherited_portlets(self):
        view = ViewEditPortletManagerRenderer(None, None, None, None)
        self.assertEqual(view.inherited_portlets(), ())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestManageContextualPortlets))
    suite.addTest(unittest.makeSuite(TestManageViewPortlets))
    suite.addTest(unittest.makeSuite(TestManageViewPortletsLinkViewlet))
    suite.addTest(unittest.makeSuite(TestViewEditPortletManagerRenderer))
    return suite
