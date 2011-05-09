"""This is an integration "unit" test.
"""

from zope.component import getMultiAdapter, getAdapters
from zope.app.component.hooks import getSite 

from Products.CMFCore.utils import getToolByName

from inqbus.bannerrotation.tests.base import BannerrotaionTestCase

import unittest


class TestSetup(BannerrotaionTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """
    
    def afterSetUp(self):
        """
        """
        
    def beforeTearDown(self):
        """
        """
        
    def test_for_created_property_sheet(self):
        """ During the install process, a folder
        with the id banners is created at the plone site root
        via GenericSetup
        """
        ptool = self.portal.portal_properties
        self.failUnless(ptool['bannerrotation_properties'])
        
    def test_for_default_properties(self):
        """ There are some default-properties.
        This test checks the default properties for beeing 
        the values defined in the properties_tool.xml and the
        right type.
        """
        ptool = self.portal.portal_properties
        bannerrotation_properties = ptool['bannerrotation_properties']
        
        # First, let check the type
        self.assertEqual(type(bannerrotation_properties.banner_source_id), str)
        self.assertEqual(type(bannerrotation_properties.enabled), bool)
        self.assertEqual(type(bannerrotation_properties.effect), str)
        self.assertEqual(type(bannerrotation_properties.random), bool)
        self.assertEqual(type(bannerrotation_properties.speed), int)
        self.assertEqual(type(bannerrotation_properties.timeout), int)
        
        # And now we can test the default values
        self.assertEqual(bannerrotation_properties.banner_source_id, 'banners')
        self.assertEqual(bannerrotation_properties.enabled, True)
        self.assertEqual(bannerrotation_properties.effect, 'fade')
        self.assertEqual(bannerrotation_properties.random, False)
        self.assertEqual(bannerrotation_properties.speed, 1000)
        self.assertEqual(bannerrotation_properties.timeout, 6000)
        
    def test_autocreation_of_banners_folder(self):
        """ During the install process, a folder
        with the id banners is created at the PloneSite root
        via GenericSetup
        """
        self.failUnless('banners' in self.portal.objectIds())
            
        
    def test_get_banners_folder(self):
        """ The Viewlet use acquisition to travers upwards until it find
        an folder with the specified source id. Here we test the default
        usage: an folder with the id "banners" at PloneSite root
        """
        self.setRoles(('Manager',)) 
        from inqbus.bannerrotation.browser.viewlets import BannerViewlet
        from Products.Five.browser import BrowserView
    
        # create a testimage in bannersfolder, because an empty folder is ignored
        self.bannersfolder_1 = self.portal.restrictedTraverse("banners")
        self.bannersfolder_1.invokeFactory("Image", "testimage")
        
        view = BrowserView(self.portal, self.portal.REQUEST)
        viewlet = BannerViewlet(self.portal, self.portal.REQUEST, view )
        viewlet.banner_source_id = "banners"
        viewlet.get_active_banners_folder()
        self.assertEqual(viewlet.get_active_banners_folder().__repr__(),
                         '<ATFolder at /plone/banners>')
        
    def test_get_deep_banners_folder(self):
        """ If there are more than one bannersfolder in the portal, he should
        use the one, he find next by acquisition.
        """
        self.setRoles(('Manager',))
        from inqbus.bannerrotation.browser.viewlets import BannerViewlet
        from Products.Five.browser import BrowserView
        
        # create subfolde and take him for context
        self.portal.invokeFactory("Folder", "testfolder_1")
        self.testfolder_1 = self.portal.restrictedTraverse("testfolder_1")
        
        # now, he should also have <ATFolder at /plone/banners>
        view = BrowserView(self.testfolder_1, self.testfolder_1.REQUEST)
        viewlet = BannerViewlet(self.testfolder_1, self.testfolder_1.REQUEST, view)
        viewlet.banner_source_id = "banners"
        self.assertEqual(viewlet.get_active_banners_folder().__repr__(),
                        '<ATFolder at /plone/banners used for /plone/testfolder_1>')
                                 
        # lets create a new subfolder. This one should still use the 
        # <ATFolder at /plone/banners>        
        self.testfolder_1.invokeFactory("Folder", "testfolder_2")
        self.testfolder_2 = self.testfolder_1.restrictedTraverse("testfolder_2")
        view = BrowserView(self.testfolder_2, self.testfolder_2.REQUEST)
        viewlet = BannerViewlet(self.testfolder_2, self.testfolder_2.REQUEST, view)
        viewlet.banner_source_id = "banners"
        self.assertEqual(viewlet.get_active_banners_folder().__repr__(),
                        '<ATFolder at /plone/banners used for ' + \
                        '/plone/testfolder_1/testfolder_2>')
                                 
        # Ok. Now we create an other banners folder in testfolder_1. After that,
        # Testfolder_1 and Testfolder_2 should use the new 
        # <ATFolder at /plone/testfolder_1/banners>
        self.testfolder_1.invokeFactory("Folder", "banners")
        view = BrowserView(self.testfolder_1, self.testfolder_1.REQUEST)
        viewlet = BannerViewlet(self.testfolder_1, self.testfolder_1.REQUEST, view)
        viewlet.banner_source_id = "banners"
        self.assertEqual(viewlet.get_active_banners_folder().__repr__(),
                        '<ATFolder at /plone/testfolder_1/banners>')
                                                       
        view = BrowserView(self.testfolder_2, self.testfolder_2.REQUEST)
        viewlet = BannerViewlet(self.testfolder_2, self.testfolder_2.REQUEST, view)
        viewlet.banner_source_id = "banners"
        self.assertEqual(viewlet.get_active_banners_folder().__repr__(),
                        '<ATFolder at /plone/testfolder_1/banners used for ' + \
                        '/plone/testfolder_1/testfolder_2>')
        
        # Finaly, lets test PloneSite root again: it still shoult use
        # <ATFolder at /plone/banners>
        view = BrowserView(self.portal, self.portal.REQUEST)
        viewlet = BannerViewlet(self.portal, self.portal.REQUEST, view )
        viewlet.banner_source_id = "banners"
        viewlet.get_active_banners_folder()
        self.assertEqual(viewlet.get_active_banners_folder().__repr__(),
                         '<ATFolder at /plone/banners>')
                         
    def test_config_form(self):
        """
        """
        # first: get all properies
        portal = getSite()
        ptool = portal.portal_properties
        effect = ptool.bannerrotation_properties.effect
        timeout = ptool.bannerrotation_properties.timeout
        speed = ptool.bannerrotation_properties.speed
        enabled = ptool.bannerrotation_properties.enabled
        random = ptool.bannerrotation_properties.random
        
        # second: get and instantiate the form
        from inqbus.bannerrotation.browser.bannerrotation_config_view import BannerrotationConfigForm
        from Products.Five.browser import BrowserView
        from plone.z3cform import z2
        form = BannerrotationConfigForm(self.portal, self.portal.REQUEST)
        z2.switch_on(form)
        form.updateWidgets()
        
        # third: check the widgets
        self.assertEqual(form.widgets['enabled'].field.default, enabled)
        self.assertEqual(form.widgets['random'].field.default, random)
        self.assertEqual(form.widgets['effect'].value, effect)
        self.assertEqual(form.widgets['timeout'].value, timeout)
        self.assertEqual(form.widgets['speed'].value, speed)

    def test_set_properties(self):
        """
        """
        from inqbus.bannerrotation.browser.bannerrotation_config_view import BannerrotationConfigView
        from plone.z3cform import z2
        # change some parts of the request for __call__()
        my_request = self.portal.REQUEST
        my_request.set('form.buttons.save', "x")
        my_request.set('form.widgets.enabled', ['true'])
        my_request.set('form.widgets.random', ['true'])
        my_request.set('form.widgets.speed', 67890)
        my_request.set('form.widgets.timeout', 12345)
        my_request.set('form.widgets.effect', ['none'])
        # instantiate the view
        view = BannerrotationConfigView(self.portal, my_request)
        view.set_properties()
        portal = getSite()
        ptool = portal.portal_properties
        self.assertEqual(ptool.bannerrotation_properties.effect, "none")
        self.assertEqual(ptool.bannerrotation_properties.enabled, True)
        self.assertEqual(ptool.bannerrotation_properties.random, True)
        self.assertEqual(ptool.bannerrotation_properties.speed, 67890)
        self.assertEqual(ptool.bannerrotation_properties.timeout, 12345)

        
def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite