from dateable.chronos.browser.month import MonthView, cmp_occurrence
from dateable.chronos.browser.interfaces import IEventDisplay
from zope.component import getMultiAdapter
from datetime import datetime

class MonthRecurringEventView(MonthView):
    """Holds the rendering information for month views"""

    def getOccurrenceDisplays(self, day):

        events =  self.getOccurrencesInDay(day)
        occurrences = []
        
        for occurrence in events:
            event = occurrence._getEvent()
            dates = event.getDates(day)
            if day in dates:
                occurrences.append(occurrence)
        
        occurrences.sort(cmp=cmp_occurrence)
        count = 0
        self.date_display_maxed[day] = 0
        displays = []
        for occurrence in occurrences:
            count += 1
            if self.calendar_tool.iseventsdisplaylimited and \
                count > self.calendar_tool.displaymaxevents:
                self.date_display_maxed[day] = 1
                break
            displays.append(getMultiAdapter([occurrence, self], IEventDisplay))
        # Cut off the last one (to be replaced by a More... tag)
        if self.date_display_maxed[day] == 1:
            displays = displays[:-1]
        return displays
    
    