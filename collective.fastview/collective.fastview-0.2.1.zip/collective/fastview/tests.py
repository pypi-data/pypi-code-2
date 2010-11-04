import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import collective.fastview

from collective.fastview.interfaces import ViewletNotFoundException

from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound

class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.fastview)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class ViewletsTestCase(TestCase):

    def test_viewlet_lookup(self):
        """
        """


        # get Viewlets view
        viewlets= self.portal.unrestrictedTraverse("@@viewlets")

        # Test direct traverse
        html = self.portal.unrestrictedTraverse("@@viewlets/plone.logo")

        self.assertTrue("portal-logo" in html)


    def test_bad_viewlet_look_up(self):
        """
        """
        try:
            viewlet = self.portal.unrestrictedTraverse("@@viewlets/foo")
            raise AssertionError("Should not be never reachec")
        except ViewletNotFoundException:
            pass
