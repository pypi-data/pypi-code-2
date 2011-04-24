#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""
"""

from datetime import datetime, date
import logging

import dateutil.tz

utc = dateutil.tz.tzutc()

local = dateutil.tz.gettz()

log = logging.getLogger(__name__)

def assign_tz(dt):
    """Make sure the datetime instance has a time zone.  Assume local.
    """
    if dt.tzinfo is None:
        # Assume local time zone
        log.debug('Adding %s time zone to %s', local, dt)
        dt = dt.replace(tzinfo=local)
        log.debug('  value after change: %s', dt)
    else:
        log.debug('%s already has time zone %s', dt, dt.tzinfo)
    return dt

def normalize_to_utc(dt):
    """
    """
    if not isinstance(dt, date):
        raise TypeError("%r is not a datetime.date instance" % (dt,))

    if isinstance(dt, datetime):
        dt = assign_tz(dt)
        dt_as_utc = dt.astimezone(utc)
        log.debug('  as utc: %s', dt_as_utc)
        return dt_as_utc
    return dt

