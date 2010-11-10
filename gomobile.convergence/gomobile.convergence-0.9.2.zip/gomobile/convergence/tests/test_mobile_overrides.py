__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.overrider.base import IOverrideStorage

from base import BaseTestCase

class TestMobileOverrides(BaseTestCase):

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")

    def create_event(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Event", "event")

    def test_get_field_list(self):
        """
        Test that we populate enabled fields vocabulary correctly from override schema.
        """

        from gomobile.convergence.overrider.base import get_field_list
        from gomobile.convergence.overrider.document import DocumentOverrideStorage
        storage = DocumentOverrideStorage()

        fields = get_field_list(storage)
        assert "Title" in fields.by_token

    def test_has_overrides(self):
        """ Document object overrides are enabled by default
        """
        self.create_doc()
        doc = self.portal.doc
        overrider = IOverrider(doc)
        assert overrider != None

        assert overrider.schema != None
        self.assertEqual(overrider._getOverrideFieldNames(), ["Title", "Description", "getText"])

        # Set one override enabled and check it is read properly
        storage = IOverrideStorage(doc)

        storage.enabled_overrides = ["Title"]
        self.assertEqual(overrider._isOverrideEnabled("Title", storage), True)
        self.assertEqual(overrider._isOverrideEnabled("Description", storage), False)

        # Set overriden title
        storage.Title = u"Foobar"

        # Call title accessor by emulator IOverrider steps
        # and see each microstep completes
        self.assertTrue(overrider._isOverride("Title"))
        storage = IOverrideStorage(self.portal.doc)
        self.assertTrue(overrider._isOverrideEnabled("Title", storage))
        self.assertEqual(overrider._getOverrideOrOrignal("Title")(), u"Foobar")

        assert overrider.Title() == u"Foobar"

    def test_has_no_overrides(self):
        """ Event object does not have default overrides
        """
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Event", "event")
        event = self.portal.event

        try:
            overrider = IOverrider(event)
            raise AssertionError("Should not be never reached")
        except TypeError:
            pass

    def test_traverse_checker(self):
        """ Check that condition view works """
        self.create_doc()
        self.create_event()


        result = self.portal.doc.restrictedTraverse("@@supports_mobile_overrides")
        result = result()
        self.assertEqual(result, True)


        result = self.portal.event.restrictedTraverse("@@supports_mobile_overrides")
        result = result()
        self.assertEqual(result, False)

    def test_render_form(self):
        self.create_doc()

        result = self.portal.doc.restrictedTraverse("@@edit_mobile_overrides")
        result()

    def test_convergence_form(self):
        self.create_doc()

        result = self.portal.doc.restrictedTraverse("@@convergence")

        self.assertEqual(result.media_status(), u"Web and mobile")

        # Test rendeing HTML without errors
        result()





def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMobileOverrides))
    return suite



