from collective.megaphonecicerolookup.tests.base import MegaphoneCiceroTestCase
from Products.Five.testbrowser import Browser


class AddressLookupTestCase(MegaphoneCiceroTestCase):
    
    def afterSetUp(self):
        # add a Megaphone with a Cicero recipient
        browser = Browser()
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic root:secret')
        browser.open('http://nohost/plone')
        browser.getLink('Megaphone Action').click()
        browser.getControl('Continue').click()
        browser.getControl('Title').value = 'Megaphone'
        browser.getControl('Continue').click()
        browser.getControl(name='crud-edit.captcha.widgets.select:list').value = ['true']
        browser.getControl('Delete').click()
        browser.getControl('Continue').click()
        browser.getLink('Add recipient').click()
        browser.getControl(name='form.widgets.recipient_type:list').value = ['cicero_address_lookup']
        browser.getControl('Continue').click()
        browser.getControl('Description of recipient').value = 'Your senators'
        browser.getControl(name='form.widgets.districtType:list').value = ['NATIONAL_UPPER']
        browser.getControl('Add Recipient').click()
        browser.open('http://nohost/plone/+/addMegaphoneAction')
        while 1:
            try:
                browser.getControl('Continue').click()
            except LookupError:
                break
        browser.getControl('Finish').click()
        browser.open('http://nohost/plone/megaphone')
        browser.getLink('Publish').click()
    
    def _submitMegaphone(self):
        # fill out the form
        self.browser = browser = Browser()
        browser.handleErrors = False
        browser.open('http://nohost/plone/megaphone')
        self.failUnless('Your senators' in browser.contents)
        browser.getControl('First Name').value = 'Harvey'
        browser.getControl('Last Name').value = 'Frank'
        browser.getControl('E-mail Address').value = 'harveyfrank@example.com'
        browser.getControl('Street').value = '1402 3rd Ave'
        browser.getControl('City').value = 'Seattle'
        browser.getControl('State').value = ['WA']
        browser.getControl('Postal Code').value = '98101'
        browser.getControl('Preview').click()
    
    def testAddressLookupIntegration(self):
        self._submitMegaphone()
        self.failUnless('Patty Murray' in self.browser.contents)

    def testAllowedStates(self):
        # don't perform lookups for any state except Indiana
        from zope.component import getUtility
        from plone.registry.interfaces import IRegistry
        from collective.megaphonecicerolookup.interfaces import IRegistrySettings
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRegistrySettings)
        settings.allowed_states = set([u'IN'])
        
        self._submitMegaphone()
        self.failIf('Patty Murray' in self.browser.contents)
