from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from datetime import timedelta, datetime
from monet.recurring_event import recurring_eventMessageFactory as _
from rt.calendarinandout.widget import CalendarInAndOutWidget

RECURRING_EVENT_SCHEMA = atapi.Schema((
         
        atapi.LinesField(
            'cadence',
            required= False,
            searchable=True,
            vocabulary='_get_days_vocab',
            widget = atapi.MultiSelectionWidget(
                format = 'checkbox',
                label=_("label_cadence", default=u"Cadence"),
                description=_("description_cadence",
                              default=u"You can set the actual days of the event in the date range specified above. If you don't set this field the event takes place every day of the week."),
                ),
            enforceVocabulary=True,
            languageIndependent=True
        ),
                                     
        atapi.LinesField(
            'except',
            required= False,
            searchable=True,
            widget = CalendarInAndOutWidget(
                label=_("label_except", default=u"Except"),
                description=_("description_field_except",
                              default=u"In this field you can set the list of days on which the event is not held. Enter the dates in the form yyyy-mm-dd."),
                auto_add=True,
                ),
            languageIndependent=True
        ),
        
))


class RecurringEventClass(object):
        
    def _get_days_vocab(self):
        return DisplayList([('0',_('Monday')),
                           ('1',_('Tuesday')),
                           ('2',_('Wednesday')),
                           ('3',_('Thursday')),
                           ('4',_('Friday')),
                           ('5',_('Saturday')),
                           ('6',_('Sunday'))])
        
    def getDates(self, day=None):
        """Main method that return all day in which the event occurs"""
        event_days = []
        blacklist = []
        
        try:
            exceptions = set(self.getExcept())
        except TypeError, e:
            self.plone_log(str(e))
            exceptions = self.getExcept()
            
        for black in sorted(exceptions):
            black = black.split('-')
            datee = datetime(int(black[0]),int(black[1]),int(black[2]))
            blacklist.append(datee.date())

        if day:
            if ((not self.getCadence() or str(day.weekday()) in self.getCadence()) 
                 and not day in blacklist):
                event_days.append(day)
            return event_days
         
        duration = (self._end_date().date() - self._start_date().date()).days

        while(duration > 0):
            day = self._end_date() - timedelta(days=duration)
            if (not self.getCadence() or str(day.weekday()) in self.getCadence()) and not day.date() in blacklist:
                event_days.append(day.date())
            duration = duration - 1
        if (not self.getCadence() or str(self._end_date().weekday()) in self.getCadence()) and not self._end_date().date() in blacklist:
            event_days.append(self._end_date().date())

        return event_days
