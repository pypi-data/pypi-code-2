import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase as ptc

from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import mfabrik.plonezohointegration

class TestEnterContactInfo(ptc.FunctionalTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(mfabrik.plonezohointegration)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
        
    def afterSetUp(self):
        """
        Show errors in console by monkey patching site error_log service
        """

        ptc.FunctionalTestCase.afterSetUp(self)

        self.browser = Browser()
        self.browser.handleErrors = False # Don't get HTTP 500 pages


        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising
        
        self.mockZohoConnection()

    def mockZohoConnection(self):
        """ Monkey patch Zoho form submissions to return always success """
        
        from mfabrik.plonezohointegration.views import ZohoContactForm
            
        def dummy(self, data):
            pass
        
        ZohoContactForm.postData = dummy
        
    def loginAsAdmin(self):
        """ Perform through-the-web login.

        Simulate going to the login form and logging in.

        We use username and password provided by PloneTestCase.

        This sets session cookie for testbrowser.
        """
        from Products.PloneTestCase.setup import portal_owner, default_password

        # Go admin
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/login_form")
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        
    
    def assertIsOnCorrectForm(self):
        """ """
        
        self.assertTrue("<h1>Contact Us</h1>" in self.browser.contents)        
        
    def goToForm(self):
        """ Open big Zoho contact form """
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/zoho-contact-form")    
        contact_form = self.browser.getForm(index=2)
        return browser, contact_form

    def test_enter_no_required_data(self):
        """ Submit form without filling it"""
        
        browser, contact_form = self.goToForm()
                
        self.assertIsOnCorrectForm()
        contact_form.submit(u"Send contact request")
        self.assertIsOnCorrectForm()
        
        self.assertTrue("Required input is missing." in self.browser.contents)
            
    def test_submit_required_fields(self):
        """ Submit ok data """
        
        browser, contact_form = self.goToForm()
        contact_form.getControl(name=u"form.widgets.first_name").value = u"Mikko"
        contact_form.getControl(name=u"form.widgets.last_name").value = u"Ohtamaa"
        contact_form.getControl(name=u"form.widgets.company").value = u"mFabrik"
        contact_form.getControl(name=u"form.widgets.email").value = u"foobar@mfabrik.com"
        self.assertIsOnCorrectForm()
        contact_form.submit(u"Send contact request")
        self.assertTrue("Thank you" in self.browser.contents)
        
    def test_enter_bad_phonenumber(self):
        """ Submit bad phone number"""
        browser, contact_form = self.goToForm()
        contact_form.getControl(name=u"form.widgets.first_name").value = u"Mikko"
        contact_form.getControl(name=u"form.widgets.last_name").value = u"Ohtamaa"
        contact_form.getControl(name=u"form.widgets.company").value = u"mFabrik"
        contact_form.getControl(name=u"form.widgets.email").value = u"foobar@mfabrik.com"
        contact_form.getControl(name=u"form.widgets.phone_number").value = u"FASDFASDF"
        contact_form.submit(u"Send contact request")
        self.assertIsOnCorrectForm()           
        self.assertTrue("Phone number contains bad characters" in self.browser.contents)
        
    def test_enter_ok_phonenumber(self):
        """ Submit bad phone number"""
        browser, contact_form = self.goToForm()
        contact_form.getControl(name=u"form.widgets.first_name").value = u"Mikko"
        contact_form.getControl(name=u"form.widgets.last_name").value = u"Ohtamaa"
        contact_form.getControl(name=u"form.widgets.company").value = u"mFabrik"
        contact_form.getControl(name=u"form.widgets.email").value = u"foobar@mfabrik.com"
        contact_form.getControl(name=u"form.widgets.phone_number").value = u"+358 (40) 123-1234"
        contact_form.submit(u"Send contact request")
        self.assertIsOnCorrectForm()
        self.assertTrue("Thank you" in self.browser.contents)
               
def test_suite():
     suite = unittest.TestSuite()
     suite.addTests([
         unittest.makeSuite(TestEnterContactInfo)
     ])
     return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
