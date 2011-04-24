#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""Filter events by a date range.
"""

import datetime
import logging
import sys

import vobject

from ical2org import tz

log = logging.getLogger(__name__)

def by_date_range(events, start, end):
    """Iterate over the incoming events and yield those that fall within the date range.
    """
    local_start = start.astimezone(tz.local)
    local_end = end.astimezone(tz.local)
    log.debug('filtering between %s (%s) and %s (%s)', start, local_start, end, local_end)
    for event in events:
        log.debug('checking %s - %s == %s for %s',
                  event.dtstart.value,
                  event.dtend.value,
                  event.summary.value,
                  getattr(event, 'uid', 'unknown UID'),
                  )

        # Add time zones to date objects so we can do proper date
        # range comparisons.
        event_start = event.dtstart.value
        event_end = event.dtend.value
        strip_times = False
        if not isinstance(event_start, datetime.datetime):
            # Convert date to datetime.

            # Remember that we need to strip the times
            # back out of the event before yielding.
            strip_times = True
            
            # Start at beginning of the start day.
            event_start = datetime.datetime.combine(event.dtstart.value,
                                                    datetime.time.min,
                                                    )

            # Because the DTEND is the non-inclusive end of the
            # event, we use the earliest time on that day when
            # there's a day or less span.  From
            # http://www.ietf.org/rfc/rfc2445.txt, section 4.6.1.
            event_end = datetime.datetime.combine(event.dtend.value,
                                                  datetime.time.min,
                                                  )

        # Convert all times to UTC for comparison
        event_start = tz.assign_tz(event_start)
        event_end = tz.assign_tz(event_end)

        # Replace the dates in case we updated the timezone
        event.dtstart.value = event_start
        event.dtend.value = event_end

        # More detailed report
#         event.prettyPrint()
#         sys.stdout.flush()

        # Look for a recurrance rule
        event_rrule = getattr(event, 'rrule', None)
        
        if event_rrule is not None:
            # Repeating event, check for occurances within the
            # time range.
            duration = event.dtend.value - event.dtstart.value
            rruleset = event.getrruleset(False)

            # Clean up timezone values in rrules.
            # Based on ShootQ calendarparser module.
            for rrule in rruleset._rrule:
                # normalize start and stop dates for each recurrance
                if rrule._dtstart:
                    rrule._dtstart = tz.assign_tz(rrule._dtstart)
                if hasattr(rrule, '_dtend') and rrule._dtend:
                    rrule._dtend = tz.assign_tz(rrule._dtend)
                if rrule._until:
                    rrule._until = tz.assign_tz(rrule._until)
            if rruleset._exdate:
                # normalize any exclusion dates
                exdates = []
                for exdate in rruleset._exdate:
                    exdate = tz.assign_tz(exdate)
                rruleset._exdate = exdates
            if hasattr(rruleset, '_tzinfo') and rruleset._tzinfo is None:
                # if the ruleset doesn't have a time zone, give it
                # the local zone
                rruleset._tzinfo = tz.local

            # Explode the event into repeats
            for recurrance in rruleset.between(local_start, local_end, inc=True):
                log.debug('Including recurrance %s', recurrance)
                dupe = event.__class__.duplicate(event)
                dupe.dtstart.value = recurrance
                dupe.dtend.value = recurrance + duration

#                 print '\nYIELDING'
#                 dupe.prettyPrint()
#                 sys.stdout.flush()
#                 event.serialize(sys.stdout)
#                 sys.stdout.flush()

                if strip_times:
                    dupe.dtstart.value = dupe.dtstart.value.date()
                    dupe.dtend.value = dupe.dtend.value.date()
                yield dupe
                
        elif event_start >= start and event_end <= end:
            # Single occurance event.
            if strip_times:
                event.dtstart.value = event.dtstart.value.date()
                event.dtend.value = event.dtend.value.date()
            yield event

        else:
            log.debug('skipping')
        
    
def unique(events):
    """Filter out duplicate events based on uid and start time.
    """
    keys = set()
    for event in events:
        key = (event.uid.value, event.dtstart.value)
        if key not in keys:
            keys.add(key)
            yield event
        else:
            log.debug('found duplicate event %s', key)
