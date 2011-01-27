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
import zope.schema.interfaces

from z3c.form import widget

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IDataConverter
from z3c.form import widget
from z3c.form import converter
from z3c.form.browser import textarea

from z3c.form.i18n import MessageFactory as _
from zamplugin.error import interfaces


class TextLinesWidget(textarea.TextAreaWidget):
    """Input type sequence widget implementation."""
    zope.interface.implementsOnly(interfaces.ITextLinesWidget)


@zope.component.adapter(zope.schema.interfaces.ITuple, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def TextLinesFieldWidget(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, TextLinesWidget(request))


class TextLinesConverter(converter.BaseDataConverter):
    """Data converter for ITextLinesWidget."""

    zope.component.adapts(
        zope.schema.interfaces.ITuple, interfaces.ITextLinesWidget)

    def toWidgetValue(self, value):
        """Convert from text lines to HTML representation."""
        widget = self.widget
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u''
        return "\n".join(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value):
            return self.field.missing_value or ()
        return tuple(value.split())
