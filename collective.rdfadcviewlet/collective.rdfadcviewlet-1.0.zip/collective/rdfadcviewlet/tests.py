import unittest

from DateTime import DateTime

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost

import collective.rdfadcviewlet


ptc.setupPloneSite()

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.rdfadcviewlet)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

from collective.rdfadcviewlet.viewlet import RDFaDublinCoreViewlet

class RDFaDCViewletTests(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        portal = self.portal
        portal.portal_properties.site_properties.exposeDCMetaTags = True

        portal.invokeFactory('Event', 'myevent',
                             title=u"My event")
        self.event = portal.myevent

    def test_viewlet(self):
        viewlet = RDFaDublinCoreViewlet(self.event, None, None, None)
        viewlet.update()

        metatags = dict(viewlet.metatags)
        self.assertEqual(metatags['dc:format'], 'text/html')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RDFaDCViewletTests))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
