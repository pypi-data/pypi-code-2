# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import logging, vobject, pytz
from coils.core  import *
from parse_vevent import parse_vevent

def get_timezoned_value(dtvalue, ctx=None):
    result = None
    if dtvalue.value.tzinfo is None:
        # start time is nieve
        if 'X-VOBJ-ORIGINAL-TZID' in dtvalue.params:
            # a timezone was specified in the file but not defined in the
            # container, lets see if we can define it on behalf of the client
            tz_name = dtvalue.params['X-VOBJ-ORIGINAL-TZID'][0]
            tz_data = None
            try:
                tz_data = pytz.timezone(tz_name)
                dtvalue.replace(tzinfo=tz_data)
            except pytz.UnknownTimeZoneError, e:
                # TODO: Implement some default behavior for unkown timezones
                # TODO: Alert user that we are unsure about the timezone (email?)
                raise e
            result = dtvalue.value.replace(tzinfo=tz_data)
    else:
        # start time has a timezone
        result = dtvalue.value
    return result

class Parser(object):

    @staticmethod
    def Parse(data, ctx, **params):
        log = logging.getLogger('parse')
        result = []
        #TODO: log duration of render at debug level
        if (data is None):
            raise CoilsException('Attempt to parse a None')
        elif (isinstance(data, str)):
            try:
                data = data.strip()
                log.debug('ICALENDAR DATA:\n\n{{{0}}}\n\n'.format(data))
                components = vobject.readComponents(data)
                log.debug('Parsed components, requesting first...')
                component = components.next()
                if (component.name == 'VEVENT'):
                    log.debug('iCalendar data is a VEVENT description.')
                    result.extend(Parser._parse_vevent1(component, ctx, log, **params))
                elif component.name == 'VCALENDAR':
                    log.debug('iCalendar data is a VCALENDAR container.')
                    try:
                        component.vevent_list
                    except Exception, e:
                        log.exception(e)
                        log.warn('VCALENDAR contains no events.')
                    else:
                        log.debug('iCalendar VCALENDAR container contains {0} events.'.format(len(component.vevent_list)))
                        for vevent in component.vevent_list:
                            result.extend(Parser._parse_vevent1(vevent, ctx, log, **params))
                else:
                    log.warn('Encountered unexpected ics component')
                    raise CoilsException('Encountered unexpected ics component')
            except Exception, e:
                log.exception(e)
                raise CoilsException('Unable to parse ics data into components.')
        else:
            raise CoilsException('Non-text data received by ics parser.')
        return result

    @staticmethod
    def _parse_vevent1(vevent, ctx, log, **params):
        utc_tz = pytz.timezone('UTC')
        starts = [ ]
        first_start = get_timezoned_value(vevent.dtstart)
        start_tz    = first_start.tzinfo
        first_start = first_start.astimezone(utc_tz)
        duration    = get_timezoned_value(vevent.dtend).astimezone(utc_tz) - first_start
        recurse_dates = vevent.getrruleset(addRDate=True)
        #if isinstance(vevent, vobject.icalendar.RecurringComponent):
        if recurse_dates is not None:
            # TODO: Support using the maximum-cycles value from defaults
            count = 50
            for start in list(recurse_dates):
                if (count < 0): break
                #starts.append(start.astimezone(utc_tz))
                start = start.replace(tzinfo=start_tz)
                start = start.astimezone(utc_tz)
                starts.append(start)
                count += -1
        else:
            starts.append(first_start)
        return parse_vevent(vevent, ctx, log, calendar=None, starts=starts, duration=duration)
