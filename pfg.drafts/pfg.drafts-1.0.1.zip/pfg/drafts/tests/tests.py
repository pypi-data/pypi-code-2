import os
import transaction
from time import sleep

from Testing import ZopeTestCase as ztc
from Testing.ZopeTestCase.utils import startZServer

from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite, onsetup

from zope.component import getAdapter
from plone.app.controlpanel.security import ISecuritySchema

@onsetup
def load_zcml():
    fiveconfigure.debug_mode = True
    import pfg.drafts
    zcml.load_config('configure.zcml', pfg.drafts)
    ztc.installPackage(pfg.drafts)
    fiveconfigure.debug_mode = False

ztc.installProduct('PloneFormGen')
load_zcml()
ptc.setupPloneSite(extension_profiles=['pfg.drafts:default'])

class SeleniumLayer(PloneSite):

    @classmethod
    def setUp(self):
        # Start up Selenium
        driver = os.environ.get('SELENIUM_DRIVER', '') or 'firefox'
        webdriver = __import__(
            'selenium.%s.webdriver' % driver, fromlist=['WebDriver'])
        args = [arg.strip() for arg in 
                os.environ.get('SELENIUM_ARGS', '').split()
                if arg.strip()]
        self.selenium = webdriver.WebDriver(*args)
        
        host, port = startZServer()
        self.base_url = 'http://%s:%s/plone' % (host, port)

    @classmethod
    def tearDown(self):
        self.selenium.quit()
        del self.selenium

class SeleniumTestCase(ptc.PloneTestCase):
    layer = SeleniumLayer

    def afterSetUp(self):
        # add a form
        self.setRoles(['Manager'])
        form = self.portal[self.portal.invokeFactory('FormFolder', 'testform')]
        form.layout = 'pfg_draft_view'
        self.portal.portal_workflow.doActionFor(form, 'publish')
        transaction.commit()
        
        # enable registration
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        security_settings.enable_user_pwd_choice = True
        
        self.base_url = self.layer.base_url
    
    def open(self, url):
        transaction.commit()
        self.layer.selenium.get(url)
    
    def test_save_draft(self):
        sel = self.layer.selenium
        
        # start filling the form
        self.open(self.base_url + '/testform')
        sel.find_element_by_name('replyto').send_keys('test@example.com')
        
        # save draft
        sel.find_element_by_link_text('register now').click()
        sleep(1)
        sel.find_element_by_name('form.fullname').send_keys('Test')
        sel.find_element_by_name('form.username').send_keys('testuser')
        sel.find_element_by_name('form.email').send_keys('test@example.com')
        sel.find_element_by_name('form.password').send_keys('password')
        sel.find_element_by_name('form.password_ctl').send_keys('password')
        sel.find_element_by_name('form.actions.register').click()
        sleep(1)
        sel.find_element_by_xpath('//input[@value="Log in"]').click()
        sleep(20)
        
        # At this point the draft should have been saved.
        self.failUnless('Draft saved.' in sel.get_page_source())
        self.failUnless(sel.get_current_url().endswith('/testform'))
        
        # Now return to the form and make sure the saved value is present.
        self.open(self.base_url + '/testform')
        value = sel.find_element_by_name('replyto').get_attribute('value')
        self.assertEqual('test@example.com', value)

        # Now log out and make sure we can return to access the form.
        self.open(self.base_url + '/logout')
        self.open(self.base_url + '/testform')
        sel.find_element_by_id('pfg-draft-login').click()
        sel.find_element_by_name('__ac_name').send_keys('testuser')
        sel.find_element_by_name('__ac_password').send_keys('password')
        sel.find_element_by_xpath('//input[@value="Log in"]').click()
        self.failUnless(sel.get_current_url().endswith('/testform'))
        value = sel.find_element_by_name('replyto').get_attribute('value')
        self.assertEqual('test@example.com', value)
