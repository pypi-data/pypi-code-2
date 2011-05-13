#
# PloneServicesCenterTestCase
#

import os
import sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneServicesCenter.tests import PloneServicesCenterTestCase

from Products.PloneServicesCenter.config import CREATE_INITIAL_CONTENT


class TestInstallation(
    PloneServicesCenterTestCase.PloneServicesCenterTestCase):

    def afterSetUp(self):
        pass

    def testPortalTypes(self):
        types = self.portal.portal_types.objectIds()
        self.failUnless('Buzz' in types)
        self.failUnless('BuzzFolder' in types)
        self.failUnless('CaseStudy' in types)
        self.failUnless('CaseStudyFolder' in types)
        self.failUnless('Provider' in types)
        self.failUnless('ProviderFolder' in types)
        self.failUnless('SiteUsingPlone' in types)
        self.failUnless('SiteUsingPloneFolder' in types)

    def testAddingBuzzFolder(self):
        self.folder.invokeFactory('BuzzFolder', 'buzz')
        items = self.folder.objectIds()
        self.failUnless('buzz' in items)

    def testAddingCaseStudyFolder(self):
        self.folder.invokeFactory('CaseStudyFolder', 'case_studies')
        items = self.folder.objectIds()
        self.failUnless('case_studies' in items)

    def testAddingProviderFolder(self):
        self.folder.invokeFactory('ProviderFolder', 'providers')
        items = self.folder.objectIds()
        self.failUnless('providers' in items)

    def testAddingSiteUsingPloneFolder(self):
        self.folder.invokeFactory('SiteUsingPloneFolder', 'plone_sites')
        items = self.folder.objectIds()
        self.failUnless('plone_sites' in items)


class TestAddingStuff(PloneServicesCenterTestCase.PloneServicesCenterTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('BuzzFolder', 'buzz')
        self.folder.invokeFactory('CaseStudyFolder', 'case_studies')
        self.folder.invokeFactory('ProviderFolder', 'providers')
        self.folder.invokeFactory('SiteUsingPloneFolder', 'plone_sites')
        self.buzz = self.folder.buzz
        self.case_studies = self.folder.case_studies
        self.providers = self.folder.providers
        self.plone_sites = self.folder.plone_sites

    def testAddingProviders(self):
        self.providers.invokeFactory('Provider', 'provider1')
        self.failUnless('provider1' in self.providers.objectIds())
        self.failUnless(self.providers.getProviders())

    def testAddingBuzz(self):
        self.buzz.invokeFactory('Buzz', 'buzz1')
        self.failUnless('buzz1' in self.buzz.objectIds())

    def testAddingCaseStudies(self):
        self.case_studies.invokeFactory('CaseStudy', 'cs1')
        self.failUnless('cs1' in self.case_studies.objectIds())
        self.failUnless(self.case_studies.getCaseStudies())

    def testAddingSites(self):
        self.plone_sites.invokeFactory('SiteUsingPlone', 'site1')
        self.failUnless('site1' in self.plone_sites.objectIds())
        self.failUnless(self.plone_sites.getSitesUsingPlone())


class TestInstallingDefaultContent(
    PloneServicesCenterTestCase.PloneServicesCenterTestCase):

    def afterSetUp(self):
        pass

    def testProvidersAdded(self):
        # a crude test that there is content in the providers folder
        if CREATE_INITIAL_CONTENT == True:
            items = self.portal.objectIds()
            self.failUnless('providers' in items)
        else:
            pass

    def testBuzzAdded(self):
        if CREATE_INITIAL_CONTENT == True:
            items = self.portal.objectIds()
            self.failUnless('buzz' in items)
        else:
            pass

    def testCaseStudiesAdded(self):
        if CREATE_INITIAL_CONTENT == True:
            items = self.portal.objectIds()
            self.failUnless('case-studies' in items)
        else:
            pass

    def testSitesAdded(self):
        if CREATE_INITIAL_CONTENT == True:
            items = self.portal.objectIds()
            self.failUnless('sites' in items)
        else:
            pass


class TestWorkflow(PloneServicesCenterTestCase.PloneServicesCenterTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser(
            'reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])

        self.folder.invokeFactory('SiteUsingPloneFolder', 'plone_sites')
        self.plone_sites = self.folder.plone_sites

    def testMemberAddsSite(self):

        self.login()
        self.plone_sites.invokeFactory('SiteUsingPlone', 'site1')
        self.failUnless('site1' in self.plone_sites.objectIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestAddingStuff))
    suite.addTest(makeSuite(TestInstallingDefaultContent))
    suite.addTest(makeSuite(TestWorkflow))
    return suite
