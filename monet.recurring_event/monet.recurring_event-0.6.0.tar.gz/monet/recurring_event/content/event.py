"""Definition of the Event content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from monet.recurring_event import recurring_eventMessageFactory as _
from monet.recurring_event.interfaces import IEvent
from monet.recurring_event.config import PROJECTNAME

from Products.ATContentTypes.content.event import ATEventSchema, ATEvent
from monet.recurring_event.content.schema import RECURRING_EVENT_SCHEMA, RecurringEventClass
from datetime import datetime, timedelta
from DateTime import DateTime

from Products.ATContentTypes.permission import ChangeEvents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from types import StringType
from cStringIO import StringIO
from Products.ATContentTypes.lib.calendarsupport import rfc2445dt, vformat, foldLine, ICS_EVENT_START, ICS_EVENT_END, VCS_EVENT_END

EventSchema = ATEventSchema.copy() + RECURRING_EVENT_SCHEMA.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

EventSchema['title'].storage = atapi.AnnotationStorage()
EventSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(EventSchema, moveDiscussion=False)
EventSchema.moveField('cadence', after='endDate')
EventSchema.moveField('except', after='cadence')
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
EventSchema.changeSchemataForField('location', 'default')
EventSchema.moveField('location', before='startDate')

EventSchema['subject'].widget.visible = {'edit': 'visible'}
EventSchema['subject'].mode = 'wr'

class RecurringEvent(ATEvent, RecurringEventClass):
    """Description of the Example Type"""
    implements(IEvent)

    meta_type = "ATEvent"
    schema = EventSchema

    #title = atapi.ATFieldProperty('title')
    #description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    security = ClassSecurityInfo()
    
    
    security.declareProtected(View, 'getVCal')
    def getVCal(self):
        """get vCal data
        """
        event_start = self._start_date().date()
        event_end = self._end_date().date()
        event_days = self.getDates()
        
        duration = (event_end - event_start).days
        intervals = []
        interval = []
        
        while(duration > 0):
            day = event_end - timedelta(days=duration)
            if day in event_days:
                if day == event_start:
                    interval.append(self._start_date())
                else:
                    interval.append(day)
            else:
                if interval:
                    intervals.append(interval)
                    interval = []
            duration = duration - 1

        if event_end in event_days:
            interval.append(self._end_date())
        if interval:
            intervals.append(interval)

        out = StringIO()
        for interval in intervals:
            startTime = interval[0]
            endTime = interval[-1]
            if not endTime == self._end_date():
                endTime = datetime(endTime.year,endTime.month,endTime.day,23,59,00)
            if not startTime == self._start_date():
                startTime = datetime(startTime.year,startTime.month,startTime.day,00,00,00)
#            if len(intervals) == 1:
#                startTime = self._start_date()
            map = {
                'dtstamp'   : rfc2445dt(DateTime()),
                'created'   : rfc2445dt(DateTime(self.CreationDate())),
                'uid'       : self.UID() + dstartformat(interval[0]),
                'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
                'summary'   : vformat(self.Title()),
                'startdate' : rfc2445dt(toDateTime(startTime)),
                'enddate'   : rfc2445dt(toDateTime(endTime)),
                }
            out.write(VCS_EVENT_START % map)
            
            description = self.Description()
            if description:
                out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    
            location = self.getLocation()
            if location:
                out.write('LOCATION:%s\n' % vformat(location))
                
            out.write(VCS_EVENT_END)
        
        return out.getvalue()
    
    
    security.declareProtected(View, 'getICal')
    def getICal(self):
        """get iCal data
        """
        event_start = self._start_date().date()
        event_end = self._end_date().date()
        event_days = self.getDates()
        
        duration = (event_end - event_start).days
        intervals = []
        interval = []
        
        while(duration > 0):
            day = event_end - timedelta(days=duration)
            if day in event_days:
                if day == event_start:
                    interval.append(self._start_date())
                else:
                    interval.append(day)
            else:
                if interval:
                    intervals.append(interval)
                    interval = []
            duration = duration - 1
 
        if event_end in event_days:
            interval.append(self._end_date())
        if interval:
            intervals.append(interval)
            
        out = StringIO()
        for interval in intervals:
            startTime = interval[0]
            endTime = interval[-1]
            if not endTime == self._end_date():
                endTime = datetime(endTime.year,endTime.month,endTime.day,23,59,00)
            if not startTime == self._start_date():
                startTime = datetime(startTime.year,startTime.month,startTime.day,00,00,00)
#            if len(intervals) == 1:
#                startTime = self._start_date()
            map = {
                'dtstamp'   : rfc2445dt(DateTime()),
                'created'   : rfc2445dt(DateTime(self.CreationDate())),
                'uid'       : self.UID() + dstartformat(interval[0]),
                'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
                'summary'   : vformat(self.Title()),
                'startdate' : rfc2445dt(toDateTime(startTime)),
                'enddate'   : rfc2445dt(toDateTime(endTime)),
                }
            out.write(ICS_EVENT_START % map)
            
            description = self.Description()
            if description:
                out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    
            location = self.getLocation()
            if location:
                out.write('LOCATION:%s\n' % vformat(location))
    
            eventType = self.getEventType()
            if eventType:
                out.write('CATEGORIES:%s\n' % ','.join(eventType))
    
            # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
            #ORGANIZER;CN=%(name):MAILTO=%(email)
            #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)
    
            cn = []
            contact = self.contact_name()
            if contact:
                cn.append(contact)
            phones = self.contact_phone()
            for phone in phones:
                cn.append(phone)
            emails = self.contact_email()
            for email in emails:
                cn.append(email)
            if cn:
                out.write('CONTACT:%s\n' % ', '.join(cn))
                
            url = self.event_url()
            if url:
                out.write('URL:%s\n' % ', '.join(url))
    
            out.write(ICS_EVENT_END)
        
        return out.getvalue()
    
    
    security.declareProtected(ChangeEvents, 'setEventType')
    def setEventType(self, value, alreadySet=False, **kw):
        """CMF compatibility method

        Changing the event type.
        """
        if type(value) is StringType:
            value = (value,)
        elif not value:
            # mostly harmless?
            value = ()
        f = self.getField('eventType')
        f.set(self, value, **kw) # set is ok

    security.declareProtected(ModifyPortalContent, 'setSubject')
    def setSubject(self, value, **kw):
        """CMF compatibility method

        Changing the subject.
        """
        f = self.getField('subject')
        f.set(self, value, **kw) # set is ok

    security.declareProtected(ModifyPortalContent, 'setExcept')
    def setExcept(self, value, **kw):
        """
        Setting exception the clean way:
         - remove dups
         - sort elements
        """
        if value is None:
            return
        f = self.getField('except')
        f.set(self, sorted(set(value)), **kw) # set is ok
        
    def post_validate(self, REQUEST, errors):
        """Check to make sure that the user give date in the right format/range"""
        
        blacklist = REQUEST.get('except', [])
        blacklist = set(blacklist)
        cadence = [int(x) for x in REQUEST.get('cadence', []) if x]

        startdate = REQUEST.get('startDate',None)
        if startdate:
            try:
                startdate = startdate.split(' ')[0].split('-')
                startdate = datetime(int(startdate[0]),int(startdate[1]),int(startdate[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')

        enddate = REQUEST.get('endDate',None)
        if enddate:
            try:
                enddate = enddate.split(' ')[0].split('-')
                enddate = datetime(int(enddate[0]),int(enddate[1]),int(enddate[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')

        # 1) Basic field validation
        for black in blacklist:
            try:
                black = black.split('-')
                datee = datetime(int(black[0]), int(black[1]), int(black[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')
                return errors

            if startdate:
                if datee < startdate:
                    errors['except'] = _("interval_except",
                                         default=u'One or more dates are not in the previous range [Start event - End event]')
                    return errors
            if enddate:
                if datee > enddate:
                    errors['except'] = _("interval_except",
                                         default=u'One or more dates are not in the previous range [Start event - End event]')
                    return errors

        # 2) Check if cadence fill event start and end
        if cadence and (startdate or enddate):
            startOk = False
            endOk = False
            for c in cadence:
                if startdate and startdate.weekday()==c:
                    startOk = True
                if enddate and enddate.weekday()==c:
                    endOk = True
            if not startOk and startdate:
                errors['startDate'] = _("cadence_bound_except_start",
                                     default=u'The start date is not a valid date because is not in the cadence set.')
                return errors
            if not endOk and enddate:
                errors['endDate'] = _("cadence_bound_except_end",
                                     default=u'The end date is not a valid date because is not in the cadence set.')
                return errors

        # 3) Check if except will not skip event start or end
        if blacklist and (startdate or enddate):
            for black in blacklist:
                black = black.split('-')
                datee = datetime(int(black[0]), int(black[1]), int(black[2])).date()
                if startdate and datee==startdate:
                    errors['startDate'] = _("except_bound_except_start",
                                         default=u'The start date is not a valid date because an except entry invalidate it.')
                    return errors
                if enddate and datee==enddate:
                    errors['endDate'] = _("except_bound_except_end",
                                         default=u'The end date is not a valid date because an except entry invalidate it.')
                    return errors

atapi.registerType(RecurringEvent, PROJECTNAME)

def toDateTime(time):
    try:
        returntime = DateTime(time.year,time.month,time.day,time.hour,time.minute,time.second)
    except AttributeError:
        returntime = DateTime(time.year,time.month,time.day)
    return returntime

def dstartformat(time):
    return toDateTime(time).strftime("%Y%m%d")

VCS_EVENT_START = """\
BEGIN:VEVENT
DTSTART:%(startdate)s
DTEND:%(enddate)s
UID:ATEvent-%(uid)s
SEQUENCE:0
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
"""
