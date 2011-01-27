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

import zope.interface
import zope.schema

from z3c.form.interfaces import ITextAreaWidget

from zam.api.i18n import MessageFactory as _



class IErrorReportingUtilityManager(zope.interface.Interface):
    """Error reporting utility schema."""

    keep_entries = zope.schema.Int(
        title=_("Keep entries"),
        description=_("Count of entries in history"),
        default=20,
        required=True)

    copy_to_zlog = zope.schema.Bool(
        title=_("Copy to log"),
        description=_("Flag for copy errors to log"),
        default=False)

    ignored_exceptions = zope.schema.Tuple(
        title=_("Ignore exceptions"),
        description=_("List of ignored exceptions"),
        value_type=zope.schema.TextLine(
            title=_("Ignored exception"),
            description=_("Name of the ignored exception."),
            default=u''),
        default=(),
        )


class ITextLinesWidget(ITextAreaWidget):
    """TextLine sequence widget."""


class IErrorReportingUtilityPage(zope.interface.Interface):
    """Error reporting utility page marker (used for menu item)."""
