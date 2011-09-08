#
# Tests UserDataPanel overrides
#

from Products.CMFPlone.tests import PloneTestCase
from base import CollectiveCPFTestCase

from zope.component import getAdapters, getMultiAdapter, getUtility

from collective.customizablePersonalizeForm.browser.personalpreferences import ExtendedUserDataPanel
from collective.customizablePersonalizeForm.adapters.interfaces import IExtendedUserDataSchema

from plone.app.users.userdataschema import IUserDataSchemaProvider

default_user = PloneTestCase.default_user

class CollectiveCPFOverridesTestCase(CollectiveCPFTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])

        self.login('manager')
                
    def testPersonalPrefsOverride(self):
        personalPrefs = getMultiAdapter((self.portal, self.portal.REQUEST), name='personal-information')
        self.failUnless(isinstance(personalPrefs, ExtendedUserDataPanel))

    def testIUserDataSchemaOverride(self):
        util = getUtility(IUserDataSchemaProvider)
        schema = util.getSchema()
        self.failUnless(schema is IExtendedUserDataSchema)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(CollectiveCPFOverridesTestCase))
    return suite
