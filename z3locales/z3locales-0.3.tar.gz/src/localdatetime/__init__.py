# Copyright (c) 2004-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from datetime import datetime
import time

from zope.i18n.locales import locales

_marker = object()


def normalize_language(lang):
    lang = lang.strip().lower()
    lang = lang.replace('_', '-')
    lang = lang.replace(' ', '')
    return lang


def get_locale_info(request):
    assert request != _marker
    accept_langs = request.get('HTTP_ACCEPT_LANGUAGE', '').split(',')

    # Normalize lang strings
    accept_langs = map(normalize_language, accept_langs)
    # Then filter out empty ones
    accept_langs = filter(None, accept_langs)

    accepts = []

    for index, lang in enumerate(accept_langs):
        l = lang.split(';', 2)

        quality = None

        if len(l) == 2:
            q = l[1]
            if q.startswith('q='):
                q = q.split('=', 2)[1]
                quality = float(q)
        else:
            # If not supplied, quality defaults to 1
            quality = 1.0

        if quality == 1.0:
            # ... but we use 1.9 - 0.001 * position to
            # keep the ordering between all items with
            # 1.0 quality, which may include items with no quality
            # defined, and items with quality defined as 1.
            quality = 1.9 - (0.001 * index)

        accepts.append((quality, l[0]))

    # Filter langs with q=0, which means
    # unwanted lang according to the spec
    # See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
    accepts = filter(lambda acc: acc[0], accepts)

    accepts.sort()
    accepts.reverse()

    return accepts[0][1] if len(accepts) else 'en'


def get_locale_dates(request=_marker, locale=_marker):
    """Return the date formatter given the request.
    """
    local_info = locale
    if local_info is _marker:
        local_info = get_locale_info(request)
    return locales.getLocale(*local_info.split('-')).dates


def get_formatted_now(request):
    """Return the current date formatted given the request local
    """
    now = time.gmtime()
    formatter = get_locale_dates(request).getFormatter('dateTime', 'full')
    return formatter.format(datetime(*now[:6]))


def get_formatted_date(
    date, size="full", request=_marker, locale=_marker, display_time=True):
    """Return a formatted date given the locale or request.

       date should be a tuple (year, month, day[, hour[, minute[,
       second]]]) or a datetime instance.
    """
    if not isinstance(date, datetime):
        date = datetime(*date)
    format = 'dateTime' if display_time else 'date'
    formatter = get_locale_dates(request, locale).getFormatter(format, size)
    return formatter.format(date)


def get_month_names(
    request=_marker, locale=_marker, calendar='gregorian'):
    """returns a list of month names for the current locale
    """
    dates = get_locale_dates(request, locale)
    return dates.calendars[calendar].getMonthNames()


def get_month_abbreviations(
    request=_marker, locale=_marker, calendar='gregorian'):
    """returns a list of abbreviated month names for the current locale
    """
    dates = get_locale_dates(request, locale)
    return dates.calendars[calendar].getMonthAbbreviations()


# BBB
getlocaleinfo = lambda self: get_locale_info(self.REQUEST)
getFormattedNow = lambda self, *args, **kwargs: get_formatted_now(
    self.REQUEST, *args, **kwargs)
getFormattedDate = lambda self, *args, **kwargs: get_formatted_date(
    self.REQUEST, *args, **kwargs)
getMonthNames = lambda self, *args, **kwargs: get_month_names(
    self.REQUEST, *args, **kwargs)
getMonthAbbreviations = lambda self, *args, **kwargs: get_month_abbreviations(
    self.REQUEST, *args, **kwargs)
