###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Scrapy items for xspider.foo project

"""

import time
import datetime

import zope.schema

import scrapy.item

_marker = object()


# datetime
DATE_STRINGS = [
    # day month year
    '%d.%m.%Y',
    '%d-%m-%Y',
    # year month day
    '%Y.%m.%d',
    '%Y-%m-%d',
    ]
TIME_STRINGS = [
    '',
    '%H',
    '%H:%M',
    '%H:%M:%S',
    ]
TIMEZONE_STRINGS = [
    '',
    ]
#DATE_FORMATS = [
#    '%d.%m.%Y',
#    '%d.%m.%Y %H:%M',
#    '%d.%m.%Y %H:%M:%S',
#    '%d-%m-%Y',
#    '%d-%m-%Y %H:%M',
#    '%d-%m-%Y %H:%M:%S',
#    ]

def getDateFormats():
    for ds in DATE_STRINGS:
        for ts in TIME_STRINGS:
            for tz in TIMEZONE_STRINGS:
                dtStr = '%s %s %s' % (ds, ts, tz)
                yield dtStr.strip()

def datetimeConverter(value):
    """Convert date time strings to a datetime object"""
    if isinstance(value, basestring):
        value = value.strip()
        # only convert a basestring
        for fmt in getDateFormats():
            try:
                tt = time.strptime(value, fmt)
                ts = time.mktime(tt)
                value = datetime.datetime.fromtimestamp(ts) 
                break
            except:
                pass
    return value


def emailConverter(value):
    """Convert anything to an email string"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = unicode(value)
    elif isinstance(value, (list, tuple)):
        value = u''.join(value)

    # strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
    return value


# int
def intConverter(value):
    """Convert anything to a list"""
    if not value:
        value = None
    elif isinstance(value, basestring):
        value = value.strip()
        value = int(value)
    return value


# list
def listConverter(value):
    """Convert anything to a list"""
    if not value:
        value = []
    elif isinstance(value, basestring):
        value = value.strip()
        value = [unicode(value)]
    elif isinstance(value, (list, tuple)):
        value = [unicode(v.strip()) for v in value if v]
    return value


# text
def textConverter(value):
    """Convert anything to textline"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = unicode(value)
    elif isinstance(value, (list, tuple)):
        value = u' '.join(value)
    # strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
    return value


# textline
def textLineConverter(value):
    """Convert anything to textline"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = unicode(value)
    elif isinstance(value, (list, tuple)):
        value = u' '.join(value)
    
    # remove line breaks and strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
        value = value.replace('\n\r', ' ')
        value = value.replace('\n', ' ')
    return value


# uri (simple non ipv-6 uri yet)
def uriConverter(value):
    """Convert anything to an uri string"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = str(value)
    elif isinstance(value, (list, tuple)):
        value = u''.join(value)

    # strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
        value = value.replace(' ', '%20')
    return value
