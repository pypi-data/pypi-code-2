##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
"""Data Converters

$Id: converter.py 98844 2009-04-03 15:26:34Z adamg $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema

from z3c.form import interfaces
from z3c.form.converter import BaseDataConverter

from mypypi.form.interfaces import ITextLinesWidget
from mypypi.form.interfaces import IMultiWidget


class TextLinesConverter(BaseDataConverter):
    """Data converter for ITextLinesWidget."""

    zope.component.adapts(
        zope.schema.interfaces.ISequence, ITextLinesWidget)

    def toWidgetValue(self, value):
        """Convert from text lines to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u''
        return u'\n'.join(unicode(v) for v in value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        if not len(value):
            return self.field.missing_value
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]
        return collectionType(valueType(v) for v in value.splitlines())

class MultiConverter(BaseDataConverter):
    """Data converter for IMultiWidget."""

    zope.component.adapts(
        zope.schema.interfaces.ISequence, IMultiWidget)

    def toWidgetValue(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return []
        # We rely on the default registered widget, this is probably a
        # restriction for custom widgets. If so use your own MultiWidget and
        # register your own converter which will get the right widget for the
        # used value_type.
        field = self.field.value_type
        widget = zope.component.getMultiAdapter((field, self.widget.request),
            interfaces.IFieldWidget)
        if interfaces.IFormAware.providedBy(self.widget):
            #form property required by objecwidget
            widget.form = self.widget.form
            zope.interface.alsoProvides(widget, interfaces.IFormAware)
        converter = zope.component.getMultiAdapter((field, widget),
            interfaces.IDataConverter)

        # we always return a list of values for the widget
        return [converter.toWidgetValue(v) for v in value]

    def toFieldValue(self, value):
        """Just dispatch it."""
        if not len(value):
            return self.field.missing_value

        field = self.field.value_type
        widget = zope.component.getMultiAdapter((field, self.widget.request),
            interfaces.IFieldWidget)
        if interfaces.IFormAware.providedBy(self.widget):
            #form property required by objecwidget
            widget.form = self.widget.form
            zope.interface.alsoProvides(widget, interfaces.IFormAware)
        converter = zope.component.getMultiAdapter((field, widget),
            interfaces.IDataConverter)

        values = [converter.toFieldValue(v) for v in value]

        # convert the field values to a tuple or list
        collectionType = self.field._type
        return collectionType(values)
