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
from z3c.i18n import MessageFactory as _
from zope.app.form import browser
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.app.form.interfaces import IInputWidget
from zope.app.form.interfaces import WidgetInputError
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form
import datetime
import zope.component
import zope.interface
import zope.schema


class DropdownWidget(browser.SelectWidget):
    """Variation of the SelectWidget that uses a drop-down list.

    This widget renders no div tags arround the select tag. This is needed
    for rendering select tags as sub widgets in the DateSelectWidget.
    """
    size = 1

    def __call__(self):
        """See IBrowserWidget."""
        value = self._getFormValue()
        contents = []
        have_results = False

        contents.append(self.renderValue(value))
        contents.append(self._emptyMarker())
        return "".join(contents)


class WidgetDataSource(object):
    """Provides a cofigurable date range source."""
    zope.interface.implements(zope.schema.interfaces.IContextSourceBinder)

    def __call__(self, context):
        """Returns a data range vocabulary."""
        yearRange = context.yearRange
        return zope.schema.vocabulary.SimpleVocabulary.fromValues(yearRange)


class IDateSelectData(zope.interface.Interface):
    """A schema used to generate a date widget."""

    year = zope.schema.Choice(
        title=_('Year'),
        description=_('The year.'),
        source=WidgetDataSource(),
        required=True)

    month = zope.schema.Choice(
        title=_('Month'),
        description=_('The month.'),
        values=range(1, 13),
        required=True)

    day = zope.schema.Choice(
        title=_('Day'),
        description=_('The day.'),
        values=range(1, 32),
        required=True)

    yearRange = zope.interface.Attribute(u"Year range.")


class DateSelectDataForDateSelectWidget(object):
    """DateSelectData for DateSelectWidget adapter

    This adapter knows how to handle get and set the day, month and year
    for a DateSelectWidget and is also able to set a the right values in
    the year vocabulary given from the yearRange attribute in the
    DateSelectWidget.
    Note: this adapter is internal used for setUpEditWidget in formlib and
    not registred in the adapter registry.
    """

    zope.interface.implements(IDateSelectData)

    def __init__(self, context, date):
        self.context = context
        self.date = date

    @apply
    def day():
        def get(self):
            return self.date.day
        def set(self, value):
            self.date.day = value
        return property(get, set)

    @apply
    def month():
        def get(self):
            return self.date.month
        def set(self, value):
            self.date.month = value
        return property(get, set)

    @apply
    def year():
        def get(self):
            return self.date.year
        def set(self, value):
            self.date.year = value
        return property(get, set)

    @property
    def yearRange(self):
        return self.context.yearRange


class DateSelectWidget(object):
    """Date Widget with multi select options."""
    zope.interface.implements(IBrowserWidget, IInputWidget)

    template = ViewPageTemplateFile('widget-date.pt')
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
    # See smart.field.IDateSelect
    yearRange = property(lambda self: self.context.yearRange)

    def __init__(self, field, request):
        self.context = field
        self.request = request
        if self.context.initialDate:
            self.initialDate = self.context.initialDate
        else:
            self.initialDate = datetime.date.today()
        value = field.query(field.context, default=self.initialDate)
        if value is None:
            # can't be None, set given start date, which is a valid value
            value = self.initialDate

        self.name = self._prefix + field.__name__

        adapters = {}
        adapters[IDateSelectData] = DateSelectDataForDateSelectWidget(self,
            value)
        self.widgets = form.setUpEditWidgets(form.FormFields(IDateSelectData),
            self.name, value, request, adapters=adapters)

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        if isinstance(value, datetime.date):
            self.widgets['year'].setRenderedValue(value.year)
            self.widgets['month'].setRenderedValue(value.month)
            self.widgets['day'].setRenderedValue(value.day)


    def setPrefix(self, prefix):
        """See zope.app.form.interfaces.IWidget"""
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__
        # Now distribute it to the sub-widgets
        for widget in [self.widgets[name]
                       for name in ['year', 'month', 'day']]:
            widget.setPrefix(self.name+'.')


    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        self._error = None
        year = self.widgets['year'].getInputValue()
        month = self.widgets['month'].getInputValue()
        day = self.widgets['day'].getInputValue()
        try:
            return datetime.date(year, month, day)
        except ValueError, v:
            self._error = WidgetInputError(
                self.context.__name__, self.label, _(v))
            raise self._error

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
        return (self.widgets['year'].hasInput() and
                (self.widgets['month'].hasInput() and
                 self.widgets['day'].hasInput()))


    def hasValidInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        return (self.widgets['year'].hasValidInput() and
            self.widgets['month'].hasValidInput() and
            self.widgets['day'].hasValidInput())


    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        output = []
        output.append(self.widgets['year'].hidden())
        output.append(self.widgets['month'].hidden())
        output.append(self.widgets['day'].hidden())
        return '\n'.join(output)


    def error(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        if self._error:
            return zope.component.getMultiAdapter(
                (self._error, self.request),
                IWidgetInputErrorView).snippet()
        year_error = self.widgets['year'].error()
        if year_error:
            return year_error
        month_error = self.widgets['month'].error()
        if month_error:
            return month_error
        day_error = self.widgets['day'].error()
        if day_error:
            return day_error
        return ""

    def __call__(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return self.template()
