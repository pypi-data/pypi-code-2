#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""
"""

import datetime
import logging

import ConfigParser

from ical2org import format, tz

log = logging.getLogger(__name__)

class OrgTreeFormatter(format.CalendarFormatter):
    """Formats output as an org outline.
    """

    def __init__(self, output, config, options):
        format.CalendarFormatter.__init__(self, output, config, options)
        self.output.write('# -*- coding: utf-8 -*-\n')
        return
    
    def start_calendar(self, calendar):
        """Begin a calendar node.
        
        Arguments:
        - `self`:
        - `calendar`:
        """
        self.active_calendar = calendar
        self.output.write('* %s' % calendar.title)
        try:
            tags = self.config.get(calendar.title, 'tags')
            tags = tags.strip(':')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            pass
        else:
            self.output.write('\t:%s:' % tags)
        self.output.write('\n')
        try:
            category = self.config.get(calendar.title, 'category')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            category = calendar.title
        self.output.write('  :CATEGORY: %s\n' % category)
        return

    def format_event(self, event):
        # Make sure the event is in our local timezone
        event_start = event.dtstart.value
        event_end = event.dtend.value
        if isinstance(event_start, datetime.datetime):
            event_start = event.dtstart.value.astimezone(tz.local)
            event_start_day = event_start.date()
        else:
            event_start_day = event.dtstart.value
            
        if isinstance(event_end, datetime.datetime):
            event_end = event.dtend.value.astimezone(tz.local)
            event_end_day = event_end.date()
        else:
            event_end_day = event_end

        # Compute the number of days over which the event occurs,
        # so we can tell if it is a single day or multi-day event.
        day_span = event_end_day - event_start_day
        log.debug('event_start %s', event_start)
        log.debug('event_end %s', event_end)
        log.debug('day_span %s', day_span)

        if not isinstance(event_start, datetime.datetime):
            log.debug('all day event')
            event_end = event_end - datetime.timedelta(1)
            if day_span <= datetime.timedelta(1):
                log.debug('single day')
                # Single day, all-day event
                time_range = event_start.strftime('<%Y-%m-%d %a>')
            else:
                # Multi-day, all-day event
                time_range = '<%s>--<%s>' % (event_start.strftime('%Y-%m-%d %a'),
                                             event_end.strftime('%Y-%m-%d %a'))
        else:
            log.debug('partial day event')
            if day_span <= datetime.timedelta(1):
                log.debug('single day')
                # Single day, partial day event
                time_range = '<%s-%s>' % (event_start.strftime('%Y-%m-%d %a %H:%M'),
                                          event_end.strftime('%H:%M'))
            else:
                # Multi-day, event at specific time
                time_range = '<%s>--<%s>' % (event_start.strftime('%Y-%m-%d %a %H:%M'),
                                             event_end.strftime('%Y-%m-%d %a %H:%M'))

        lines = ['** %s\n   %s' % (event.summary.value, time_range) ]

        if getattr(event, 'uid', None):
            lines.extend(['   :PROPERTIES:',
                          '   UID: %s' % event.uid.value,
                          '   :END:',
                          ])

        if getattr(event, 'location', None):
            lines.append('   - Location: %s' % event.location.value)

        if getattr(event, 'description', None):
            desc_lines = event.description.value.splitlines()
            if desc_lines:
                lines.append('   - %s' % desc_lines[0])
                lines.extend([ '     %s' % l for l in desc_lines[1:]])

        lines.append('')
        return '\n'.join(lines)
    



        

