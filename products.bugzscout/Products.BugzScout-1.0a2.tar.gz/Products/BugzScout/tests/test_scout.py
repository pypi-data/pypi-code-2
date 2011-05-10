# -*- coding: utf-8 -*-
from Products.BugzScout.tests import unittest
from Products.BugzScout.tests.base import BUGZSCOUT_INTEGRATION_TESTING, \
    create_mock_reporter
from zope.component import getMultiAdapter, getUtility
from zope.component.globalregistry import globalSiteManager
from plone.registry.interfaces import IRegistry


class ScoutTest(unittest.TestCase):
    """Test to see if the scout view adapter catches the exceptions
    reports them to a FogBugz instance (mock fogbugz in this case)."""

    layer = BUGZSCOUT_INTEGRATION_TESTING

    def setUp(self):
        #: Initialize the variable we will use in the following mock function.
        self.error_handler_values = dict()
        #: Register a mock bugz reporter.
        mock_reporter = create_mock_reporter(self.error_handler_values)
        from Products.BugzScout.interfaces import IBugzScoutReporter
        globalSiteManager.registerUtility(mock_reporter, IBugzScoutReporter)
        #: Local assignments for easy reference
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        #: Plone registry values assigned for easy reference
        plone_registry = getUtility(IRegistry)
        prefix = 'Products.BugzScout.'
        self._testing_uri = plone_registry['%suri' % prefix]
        self._testing_username = plone_registry['%susername' % prefix]
        self._testing_project = plone_registry['%sproject' % prefix]
        self._testing_area = plone_registry['%sarea' % prefix]
        #: Plone MailHost email address
        self._testing_email = self.portal.getProperty('email_from_address')

    def tearDown(self):
        from Products.BugzScout.interfaces import IBugzScoutReporter
        globalSiteManager.registerUtility(provided=IBugzScoutReporter)
        del self.error_handler_values

    def test_reports_to_fogbugz(self):
        """Call scout view adapter directly."""
        from Products.BugzScout.interfaces import IRequestExceptionHandler
        scout_view = getMultiAdapter((self.portal, self.request),
                                     name='error_handler')
        expected_values = dict(error_type='ErrOr_tYpE', error_tb='ErrOr_tb',
                               error_log_url='ErrOr_lOg_Url' )
        scout_view(**expected_values)
        description = self.error_handler_values['description']
        #: Check for passed in values.
        for key, value in expected_values.iteritems():
            assert description.find(value) >= 0, \
                   "%s's value (%s) not found in the description." \
                   % (key, value)
        #: Check for derived values.
        self.assertEqual(self.error_handler_values['uri'], self._testing_uri)
        self.assertEqual(self.error_handler_values['username'], self._testing_username)
        self.assertEqual(self.error_handler_values['project'], self._testing_project)
        self.assertEqual(self.error_handler_values['area'], self._testing_area)
        self.assertEqual(self.error_handler_values['email'], self._testing_email)

    def test_error_handler_triggered(self):
        """Call standard_error_message to check that our error handler has
        been triggered as part of the message process."""
        std_err_msg = self.portal.restrictedTraverse('standard_error_message')
        #: Set up some essential variables that must be passed to
        #  standard_error_message for the test to operate.
        error_type = 'BogusError'
        error_message = 'BogusError(bogus != valid)'
        error_id = 'abc123'
        error_log_url = 'http://nohost/error_log?id=%s' % error_id
        error_tb = "traceback\nfailed to find_wallet()"
        #: The above test is comprehensive enough that we don't need to exam
        #  that all the values have been set. We will however check that one
        #  gets set and that the default_error_message page is rendered.
        error_page = std_err_msg(error_type=error_type,
                                 error_message=error_message,
                                 error_log_url=error_log_url,
                                 error_tb=error_tb)
        #: Test the assigned value.
        description = self.error_handler_values['description']
        assert description.find(error_type) >= 0, \
               "Description assignment not found."
        #: Test the rendered results
        assert error_page.find(error_id) >= 0, \
               "Rendered error page was not rendered corrrectly:\n\n%s" \
               % error_page
