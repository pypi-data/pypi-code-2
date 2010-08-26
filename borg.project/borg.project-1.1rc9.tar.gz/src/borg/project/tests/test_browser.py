from mechanize._mechanize import LinkNotFoundError
import unittest

from Products.Five.testbrowser import Browser
from Products.PloneTestCase.setup import portal_owner, default_password

from base import BorgProjectFunctionalTestCase

def getBrowser(url):
    browser = Browser()
    browser.open(url)
    try:
        browser.getLink('Log in').click()
    except LinkNotFoundError:
        #!Plone4
        pass
    browser.getControl(name='__ac_name').value = portal_owner
    browser.getControl(name='__ac_password').value = default_password
    browser.getControl(name='submit').click()
    return browser

class BrowserTests(BorgProjectFunctionalTestCase):
    def afterSetUp(self):
        super(BrowserTests, self).afterSetUp()
        self.portal_url = self.portal.absolute_url()
        self.browser = getBrowser(self.portal.absolute_url())
        self.browser.handleErrors = False

    def test_Views(self):
        title = 'test title'
        description = 'test description'
        self.browser.getLink('Project workspace').click()
        self.browser.getControl(name='form.title').value = title
        self.browser.getControl(name='form.description').value = description
        self.browser.getControl(name="form.workflow_policy").value = ['Default project workflow']
        self.browser.getControl('Save').click()
        self.assertTrue('There are currently no items in this folder.' in 
                        self.browser.contents)
        self.assertEqual(self.browser.url.split('/')[4], 'test-title')
        self.assertTrue(title in self.browser.contents)
        self.assertTrue(description in self.browser.contents)

def test_suite():
    return unittest.makeSuite(BrowserTests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


