import unittest
import doctest
from Testing import ZopeTestCase as ztc
from collective.langMailHost.tests import base
from Products.CMFCore.utils import getToolByName

from Acquisition import aq_base
from zope.component import getSiteManager
from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost

class langMockMailHost(MockMailHost):
    smtp_host = 'localhost'

class TestSetup(base.MailHostFunctionalTestCase):

    def afterSetUp( self ):
        """After SetUp"""
        portal = self.portal
        language_tool = getToolByName(portal, 'portal_languages')
        language_tool.addSupportedLanguage('ja')


        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = langMockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)

def test_suite():
    return unittest.TestSuite([

        # Functional tests for adapters.
        ztc.FunctionalDocFileSuite(
            'tests/functional/adapter.txt', package='collective.langMailHost',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Functional tests for sending mails.
        ztc.FunctionalDocFileSuite(
            'tests/functional/send.txt', package='collective.langMailHost',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
