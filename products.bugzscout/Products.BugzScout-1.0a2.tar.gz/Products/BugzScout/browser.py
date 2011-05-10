# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite
from plone.registry.interfaces import IRegistry
from Products.BugzScout.interfaces import IRequestExceptionHandler, \
    IBugzScoutReporter


class RequestExceptionHandler(object):
    implements(IRequestExceptionHandler)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, error_type=None, error_message=None,
                 error_log_url=None, error_tb=None, error_traceback=None,
                 error_value=None):
        #: Report the bug to FogBugz
        self._report_bug(error_type, error_tb, error_log_url)

    def _report_bug(self, type, traceback, log_url=None):
        """Report bug to FogBugz"""
        reporter = getUtility(IBugzScoutReporter)
        plone_registry = getUtility(IRegistry)
        registry_prefix = 'Products.BugzScout.'
        uri = plone_registry['%suri' % registry_prefix]
        username = plone_registry['%susername' % registry_prefix]
        project = plone_registry['%sproject' % registry_prefix]
        area = plone_registry['%sarea' % registry_prefix]
        email = getSite().getProperty('email_from_address')
        # XXX desc. place holder
        description = '\n\n'.join([type, traceback, log_url])
        return reporter.report(uri, username, email, project, area,
                               description)

