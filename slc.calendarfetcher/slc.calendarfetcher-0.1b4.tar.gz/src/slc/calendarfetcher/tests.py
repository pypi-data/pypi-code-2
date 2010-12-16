import unittest

from zope import component
from zope.interface import alsoProvides
from zope.annotation.interfaces import IAnnotations
from Testing import ZopeTestCase as ztc

from plone import browserlayer
from plone.browserlayer import utils as browserlayerutils

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.CMFCore.utils import getToolByName
from slc.calendarfetcher.browser.interfaces import ICalendarFetcherLayer

from p4a.calendar.interfaces import ICalendarEnhanced

PRODUCTS = [
        'plone.z3cform',
        'Calendaring',
        'p4a.calendar',
        'p4a.plonecalendar',
        'p4a.subtyper',
        'slc.calendarfetcher',
        ]
ptc.setupPloneSite(products=PRODUCTS)
ztc.installProduct('Marshall')
ztc.installProduct('Calendaring')

class CalendarFetcherTestLayer(PloneSite):

    @classmethod
    def setUp(cls):
        """ """
        fiveconfigure.debug_mode = True
        import slc.calendarfetcher
        zcml.load_config('configure.zcml', slc.calendarfetcher)
        fiveconfigure.debug_mode = False
        ztc.installPackage('slc.calendarfetcher')
        browserlayerutils.register_layer(
                                ICalendarFetcherLayer,
                                name='slc.calendarfetcher'
                                )
        PloneSite.setUp()


class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    layer = CalendarFetcherTestLayer 


class TestFetcher(TestCase):

    def afterSetUp(self):
        """ """
        self.loginAsPortalOwner()
        portal = self.portal
        portal.invokeFactory('Folder', 'calendar', title="Calendar")
        calendar = getattr(portal, 'calendar')
        annotations = IAnnotations(calendar)
        annotations['slc.calendarfetcher-urls'] = [
            'http://www.google.com/calendar/ical/german__en%40holiday.calendar.google.com/public/basic.ics',
            'http://www.google.com/calendar/ical/sa__en%40holiday.calendar.google.com/public/basic.ics',
            ]
        alsoProvides(calendar, ICalendarEnhanced)


    def test_calendarfetcher(self):
        """ Tests:
            slc.calendarfetcher.browser.calendarfetcher.CalendarFetcherUtils 
        """
        portal = self.portal
        calendar = getattr(portal, 'calendar')
        request = self.folder.REQUEST

        qi = getToolByName(self.portal, 'portal_quickinstaller')
        assert(qi.isProductInstallable('slc.calendarfetcher'))
        assert(qi.isProductInstalled('slc.calendarfetcher'))
        assert(ICalendarFetcherLayer in browserlayer.utils.registered_layers())
        # FIXME:
        # Doesn't find the view unless I remove the "layer" attr in the
        # <browser:page> declaration in slc.calendarfetcher.browser.configure.zcml
        # 
        # The layer is however being registered, I make sure of that in the 'setUp' method
        # and I test for it above. So I'm at a loss as to what is the problem
        # here...

        # This returns None, even if the layer is not required... wierd
        # view = component.queryMultiAdapter(
        #                 (self.portal.calendar, self.portal.calendar.REQUEST),
        #                 name='@@calendarfetcher_utils')

        # Only works when browserlayer requirement is removed.
        # So for now when I test, I first remove it manually. Blegh! 
        view = self.portal.calendar.restrictedTraverse('@@calendarfetcher_utils')

        view.fetch_remote_calendars()
        self.assertEquals(len(calendar.objectValues()) !=  0, True)

        calendar.manage_delObjects(calendar.objectIds())
        self.assertEquals(len(calendar.objectValues()), 0)

        view.fetch_all_remote_calendars()
        self.assertEquals(len(calendar.objectValues()) !=  0, True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFetcher))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

