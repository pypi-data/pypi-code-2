# -*- coding: utf-8 -*-
from zope.interface import Interface


class IExceptionHandler(Interface):
    """Handle any type of exception on a context."""


class IRequestExceptionHandler(IExceptionHandler):
    """Handle request oriented exceptions."""


class IBugzScoutReporter(Interface):
    """Callable that reports a bug to a FogBugz instance."""

    def report(uri, username, email, project, area, description):
        """Report the bug"""
