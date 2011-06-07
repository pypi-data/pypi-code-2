##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Datetime widget

$Id: datetimewidget.py 4368 2005-12-08 22:19:15Z gary $
"""
import datetime

from zope.schema import TextLine, Bool, Int, Date, Choice
from zope.schema import getFieldsInOrder
from zope.interface import Interface, implements
from zope.interface.common.idatetime import ITZInfo
from zope.datetime import parseDatetimetz, DateTimeError
from zope.app.form.browser import textwidgets
from zope.app.form.browser.widget import renderElement
import zope.datetime
import zc.i18n.date
import zc.resourcelibrary
import glob
import os


# initialize the language files
LANGS = []
for langFile in glob.glob(
    os.path.join(os.path.dirname(__file__),'resources','languages') + '/calendar-??.js'):
    LANGS.append(os.path.basename(langFile)[9:11])

def normalizeDateTime(dt, request):
    if dt is not None:
        if (dt.tzinfo is not None and
            isinstance(dt.tzinfo, zope.datetime._tzinfo)):
            tzinfo = ITZInfo(request)
            dt = dt.replace(tzinfo=None) # TODO: this is a hack
            # to accomodate pre-Zope-3.2 datetime widgets that assume UTC
            # timezone.  Zope 3.2+ datetime widgets should use the
            # request's timezone, or pytz.utc for UTC rather than the
            # datetimeutils version.
        dt = zc.i18n.date.normalize(request, dt)
    return dt

def localizeDateTime(dt, request):
    if (isinstance(dt, datetime.datetime) and
        dt.tzinfo is not None and
        dt.tzinfo.utcoffset(None) == datetime.timedelta(0)):

        tzinfo = ITZInfo(request, None)
        if tzinfo is not None:
            dt = dt.astimezone(tzinfo)
    return dt


class JavascriptObject(TextLine):
    pass


class ICalendarWidgetConfiguration(Interface):
    """Configuration schema for the calendar widget.

    See http://www.dynarch.com/demos/jscalendar/doc/html/
        reference.html#node_sec_2.1
    """

    inputField = TextLine(
        title=u"Id of input field",
        default=None,
        required=False)
    displayArea = TextLine(
        title=u"Id of element which displays the date",
        default=None,
        required=False)
    button = TextLine(
        title=u"Id of trigger",
        default=None,
        required=False)
    eventName = TextLine(
        title=u"Event name of trigger",
        default=u'click',
        required=False)
    ifFormat = TextLine(
        title=u"Input field date format",
        default=u'%Y/%m/%d')
    daFormat = TextLine(
        title=u"displayArea date format",
        default=u'%Y/%m/%d')
    singleClick = Bool(
        title=u"Calendar is in single-click mode",
        default=True)
    # disableFunc - deprecated
    dateStatusFunc = JavascriptObject(
        title=u"Date status function",
        description=u"""
        A function that receives a JS Date object and returns a boolean or a
        string. This function allows one to set a certain CSS class to some
        date, therefore making it look different. If it returns true then the
        date will be disabled. If it returns false nothing special happens with
        the given date. If it returns a string then that will be taken as a CSS
        class and appended to the date element. If this string is ``disabled''
        then the date is also disabled (therefore is like returning true).
        """,
        default=None,
        required=False)
    firstDay = Int(
        title=u"First day of week (0 is Sunday, 1 is Monday, 6 is Saturday)",
        default=0)
    weekNumbers = Bool(
        title=u"Display week numbers",
        default=True)
    align = TextLine(
        title=u"Alingment of calendar",
        default=u'Bl')
    range = TextLine(
        title=u"Range of allowed years",
        default=u"[1900, 2999]")
    flat = TextLine(
        title=u"Id of parent object for flat calendars",
        default=None,
        required=False)
    flatCallback = TextLine(
        title=u"Function to call when the calendar is changed",
        default=None)
    onSelect = TextLine(
        title=u"Custom click-on-date handler",
        default=None,
        required=False)
    onClose = JavascriptObject(
        title=u"Custom handler of 'calendar closed' event",
        default=None,
        required=False)
    onUpdate = JavascriptObject(
        title=u"Custom handler of 'calendar updated' event",
        default=None,
        required=False)
    date = Date(
        title=u"Initial date",
        default=None,
        required=False)
    showsTime = Bool(
        title=u"Show time",
        default=False)
    timeFormat = Choice(
        title=u"Time format (12 hours / 24 hours)",
        values=['12', '24'],
        default='24')
    electric = Bool(
        title=u"Update date field only when calendar is closed",
        default=True)
    position = TextLine(
        title=u"Default [x, y] position of calendar",
        default=None,
        required=False)
    cache = Bool(
        title=u"Cache calendar object",
        default=False)
    showOthers = Bool(
        title=u"Show days belonging to other months",
        default=False)
    multiple = JavascriptObject(
        title=u"Multiple dates",
        description=u"""
        A JavaScript list of dates that stores the dates to be preselected
        on the widget.
        """,
        default=None)



class CalendarWidgetConfiguration(object):
    implements(ICalendarWidgetConfiguration)

    _multiple_dates = None

    def __init__(self, name, **kw):
        self.name = name.replace('.', '_')
        for name, field in getFieldsInOrder(ICalendarWidgetConfiguration):
            if name in kw:
                value = kw.pop(name)
            else:
                value = field.default
            setattr(self, name, value)
        if kw:
            raise ValueError('unknown arguments: %s' % ', '.join(kw.keys()))

    def setMultiple(self, dates):
        self._multiple_dates = dates
        self.multiple = 'multi_%s' % self.name
        self.onClose = ('getMultipleDateClosedHandler("%s", multi_%s)'
                        % (self.inputField, self.name))

    def setEnabledWeekdays(self, enabled_weekdays):
        """Enable just a set of weekdays.

        `enabled_weekdays` is a list of ints (0 = Sunday, 1 = Monday).
        """
        weekdays = ', '.join(str(weekday) for weekday in enabled_weekdays)
        self.dateStatusFunc = 'enabledWeekdays([%s])' % weekdays

    def dumpJS(self):
        """Dump configuration as a JavaScript Calendar.setup call."""
        rows = []
        for name, field in getFieldsInOrder(ICalendarWidgetConfiguration):
            value = getattr(self, name)
            if value != field.default:
                if value is None:
                    value_repr = 'null'
                elif isinstance(field, JavascriptObject):
                    value_repr = str(value)
                elif isinstance(value, basestring):
                    value_repr = repr(str(value))
                elif isinstance(value, bool):
                    value_repr = value and 'true' or 'false'
                elif isinstance(value, datetime.date):
                    value_repr = 'new Date(%d, %d, %d)' % (value.year,
                                                       value.month-1, value.day)
                else:
                    raise ValueError(value)
                row = '  %s: %s,' % (name, value_repr)
                rows.append(row)
        if rows:
            rows[-1] = rows[-1][:-1] # remove last comma
        return "Calendar.setup({\n" + '\n'.join(rows) + '\n});\n'


template = """
%(widget_html)s
<input type="button" value="..." id="%(trigger_name)s">
<script type="text/javascript">
  %(langDef)s
  %(multiple_init)s
  %(calendarSetup)s
</script>
"""


class DatetimeBase(object):

    enabled_weekdays = None

    def __call__(self):
        widget_html = super(DatetimeBase, self).__call__()
        return self._render(widget_html)

    def hidden(self):
        """Render the widget with the actual date list field hidden."""
        widget_html = super(DatetimeBase, self).hidden()
        return self._render(widget_html)

    def _render(self, widget_html):
        """Render the date widget.

        `widget_html` is the HTML for the simple date field.  This method
        wraps that field in some extra code for the advanced JavaScript widget.
        """
        zc.resourcelibrary.need('zc.datetimewidget')
        lang = self.request.locale.id.language
        lang = lang in LANGS and lang or 'en'
        if lang != 'en':
            # en is always loaded via the resourcelibrary, so that all
            # variables are defined in js
            # TODO: do not hardcode this
            langFile = '/++resource++zc.datetimewidget/'\
                    'languages/calendar-%s.js' % lang
            langDef = "dateTimeWidgetLoadLanguageFile('%s');" % langFile
        else:
            langDef = ''

        conf = self._configuration()
        trigger_name = '%s_trigger' % self.name

        multiple_init = ''
        if getattr(conf, 'multiple', None):
            initial_dates = self.datesInJS(conf._multiple_dates)
            multi_varname = 'multi_' + self.name.replace('.', '_')
            multiple_init = 'var %s = %s;' % (multi_varname, initial_dates)

        return template % dict(widget_html=widget_html,
                               trigger_name=trigger_name,
                               langDef=langDef,
                               multiple_init=multiple_init,
                               calendarSetup=conf.dumpJS())

    def datesInJS(self, dates):
        """Return a list of dates in JavaScript-ready format.

        `dates` may be None or a set of datetime.date() objects.
        """
        if not dates:
            return '[]'

        date_reprs = ['new Date(%d, %d, %d)' % (dt.year, dt.month-1, dt.day)
                      for dt in sorted(dates)]
        return '[' + ', '.join(date_reprs) + ']'

    def _configuration(self):
        trigger_name = '%s_trigger' % self.name
        conf = CalendarWidgetConfiguration(self.name,
                                           showsTime=self._showsTime,
                                           ifFormat=self._format,
                                           button=trigger_name,
                                           inputField=self.name)
        if self.enabled_weekdays is not None:
            conf.setEnabledWeekdays(self.enabled_weekdays)
        return conf

    def setEnabledWeekdays(self, enabled_weekdays):
        """Enable only particular weekdays.

        Other weekdays will simply not be selectable in the calendar
        widget.

        `enabled_weekdays` is a set of integers (0 = Sunday, 1 = Monday).
        """
        self.enabled_weekdays = enabled_weekdays

    def _toFieldValue(self, input):
        # TODO: Manually check if weekday is enabled -- the user could have
        # directly entered the date.
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                dt = parseDatetimetz(input)
            except (DateTimeError, ValueError, IndexError), v:
                return super(DatetimeBase, self)._toFieldValue(input)
            else:
                if self._showsTime:
                    return dt
                else:
                    return dt.date()

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        if value:
            value = localizeDateTime(value, self.request)
            return value.strftime(self._format)
        else:
            return u''


class DatetimeWidget(DatetimeBase, textwidgets.DatetimeWidget):
    """Datetime entry widget."""

    _format = '%Y-%m-%d %H:%M:%S'
    _showsTime = True

    def _toFieldValue(self, input):
        res = super(DatetimeWidget, self)._toFieldValue(input)
        if res is not self.context.missing_value:
            res = normalizeDateTime(res, self.request)
        return res


class DateWidget(DatetimeBase, textwidgets.DateWidget):
    """Date entry widget."""

    displayWidth = 10

    _format = '%Y-%m-%d'
    _showsTime = False


class DateSetWidget(DatetimeBase, textwidgets.DateWidget):
    """Widget for entry of sets of dates."""

    displayWidth = 30

    _format = '%Y-%m-%d'
    _showsTime = False

    def __init__(self, field, item, request):
        super(DateSetWidget, self).__init__(field, request)

    def _configuration(self):
        conf = DatetimeBase._configuration(self)
        value = self.context.query(self.context.context, default=[])
        conf.setMultiple(value)
        return conf

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            dates = input.split()
            values = set()
            for date in dates:
                value = super(DateSetWidget, self)._toFieldValue(date)
                values.add(value)
        return values

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing

        date_strs = [super(DateSetWidget, self)._toFormValue(date)
                     for date in sorted(value)]
        return ' '.join(date_strs)


class DatetimeDisplayBase(object):

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if content == self.context.missing_value:
            return ""
        content = localizeDateTime(content, self.request)
        formatter = self.request.locale.dates.getFormatter(
            self._category, (self.displayStyle or None))
        content = formatter.format(content)
        return renderElement("span", contents=textwidgets.escape(content),
                             cssClass=self.cssClass)

class DatetimeDisplayWidget(
    DatetimeDisplayBase, textwidgets.DatetimeDisplayWidget):
    pass

class DateDisplayWidget(DatetimeDisplayBase, textwidgets.DateDisplayWidget):
    pass
