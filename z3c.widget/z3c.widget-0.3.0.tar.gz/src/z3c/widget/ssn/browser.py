##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
__docformat__ = 'reStructuredText'

from z3c.i18n import MessageFactory as _
from zope.app.form import browser
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.app.form.interfaces import IInputWidget
from zope.app.form.interfaces import WidgetInputError
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form
import datetime
import re
import zope.component
import zope.interface
import zope.schema


class ISSNData(zope.interface.Interface):
    """A schema used to generate a SSN widget."""

    first = zope.schema.TextLine(
        title=_('Frst three digits'),
        description=_('The first three digits of the SSN.'),
        min_length=3,
        max_length=3,
        constraint=re.compile(r'^[0-9]{3}$').search,
        required=True)

    second = zope.schema.TextLine(
        title=_('Second two digits'),
        description=_('The second two digits of the SSN.'),
        min_length=2,
        max_length=2,
        constraint=re.compile(r'^[0-9]{2}$').search,
        required=True)

    third = zope.schema.TextLine(
        title=_('Third four digits'),
        description=_('The third four digits of the SSN.'),
        min_length=4,
        max_length=4,
        constraint=re.compile(r'^[0-9]{4}$').search,
        required=True)


class SSNWidgetData(object):
    """Social Security Number Data"""
    zope.interface.implements(ISSNData)

    first = None
    second = None
    third = None

    def __init__(self, context, number=None):
        self.context = context
        if number:
            self.first, self.second, self.third = number.split('-')

    @property
    def number(self):
        return u'-'.join((self.first, self.second, self.third))


class SSNWidget(object):
    """Social Security Number Widget"""
    zope.interface.implements(IBrowserWidget, IInputWidget)

    template = ViewPageTemplateFile('widget-ssn.pt')
    _prefix = 'field.'
    _error = None
    widgets = {}

    # See zope.app.form.interfaces.IWidget
    name = None
    label = property(lambda self: self.context.title)
    hint = property(lambda self: self.context.description)
    visible = True
    # See zope.app.form.interfaces.IInputWidget
    required = property(lambda self: self.context.required)

    def __init__(self, field, request):
        self.context = field
        self.request = request
        self.name = self._prefix + field.__name__

        value = field.query(field.context)
        adapters = {}
        adapters[ISSNData] = SSNWidgetData(self, value)
        self.widgets = form.setUpEditWidgets(
            form.FormFields(ISSNData),
            self.name, value, request, adapters=adapters)
        self.widgets['first'].displayWidth = 3
        self.widgets['second'].displayWidth = 2
        self.widgets['third'].displayWidth = 4

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        if isinstance(value, unicode):
            first, second, third = value.split('-')
            self.widgets['first'].setRenderedValue(first)
            self.widgets['second'].setRenderedValue(second)
            self.widgets['third'].setRenderedValue(third)


    def setPrefix(self, prefix):
        """See zope.app.form.interfaces.IWidget"""
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__
        # Now distribute it to the sub-widgets
        for widget in [
                self.widgets[name] for name in ['first', 'second', 'third']]:
            widget.setPrefix(self.name+'.')


    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        self._error = None
        try:
            return u'-'.join((
                self.widgets['first'].getInputValue(),
                self.widgets['second'].getInputValue(),
                self.widgets['third'].getInputValue() ))
        except ValueError, v:
            self._error = WidgetInputError(
                self.context.__name__, self.label, _(v))
            raise self._error
        except WidgetInputError, e:
            self._error = e
            raise e


    def applyChanges(self, content):
        """See zope.app.form.interfaces.IInputWidget"""
        field = self.context
        new_value = self.getInputValue()
        old_value = field.query(content, self)
        # The selection has not changed
        if new_value == old_value:
            return False
        field.set(content, new_value)
        return True


    def hasInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        return (self.widgets['first'].hasInput() and
                (self.widgets['second'].hasInput() and
                 self.widgets['third'].hasInput()))


    def hasValidInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        return (self.widgets['first'].hasValidInput() and
            self.widgets['second'].hasValidInput() and
            self.widgets['third'].hasValidInput())


    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        output = []
        output.append(self.widgets['first'].hidden())
        output.append(self.widgets['second'].hidden())
        output.append(self.widgets['third'].hidden())
        return '\n'.join(output)


    def error(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        if self._error:
            return zope.component.getMultiAdapter(
                (self._error, self.request),
                IWidgetInputErrorView).snippet()
        first_error = self.widgets['first'].error()
        if first_error:
            return first_error
        second_error = self.widgets['second'].error()
        if second_error:
            return second_error
        third_error = self.widgets['third'].error()
        if third_error:
            return third_error
        return ""

    def __call__(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return self.template()
