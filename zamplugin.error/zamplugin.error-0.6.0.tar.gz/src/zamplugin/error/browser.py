##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('zam')

from z3c.formui import form
from z3c.form import field
from z3c.form import button
from z3c.pagelet import browser

from zamplugin.error import interfaces
from zamplugin.error import widget


class EditErrorLog(form.EditForm):

    zope.interface.implements(interfaces.IErrorReportingUtilityPage)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')

    fields = field.Fields(interfaces.IErrorReportingUtilityManager)

    fields['ignored_exceptions'].widgetFactory = widget.TextLinesFieldWidget


class Errors(browser.BrowserPagelet):
    """Error listing page."""

    zope.interface.implements(interfaces.IErrorReportingUtilityPage)

    @property
    def values(self):
        return self.context.getLogEntries()


class Error(browser.BrowserPagelet):
    """Show error page."""

    zope.interface.implements(interfaces.IErrorReportingUtilityPage)

    errorId = None

    @property
    def logEntry(self):
        """Return log entry if given in request."""
        if self.errorId is not None:
            return self.context.getLogEntryById(self.errorId)

    def update(self):
        self.errorId = self.request.get('id')
        super(Error, self).update()


class ErrorAsText(Error):
    """Show error as text."""