import itertools
from Acquisition import aq_inner
from Acquisition import aq_chain
from zope.interface import implements
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions 
from zope import schema
from zope.formlib import form
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote_plus
from time import localtime
from zope.i18nmessageid import MessageFactory
from DateTime import DateTime
from Products.SimpleBlog.interfaces import IBlog
from Products.SimpleBlog.Permissions import VIEW_PORTLET_PERMISSION

PLMF = MessageFactory('plonelocales')

class ISimpleBlogPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    showCalendar = schema.Bool(title=_(u'Show calendar'),
                                               required=True, default=True)
    showRecent = schema.Bool(title=_(u'Show recent blog posts'), required=True, default=True)
    maxResults = schema.Int(title=_(u'Number of recent posts to display '),
                       required=True,
                       default=5)    
    showCategories = schema.Bool(title=_(u'Show categories'), 
                                                 description=_(u'Displays all the categories and the number of posts within the category'),
                                                 required=True, 
                                                 default=True)
    showComments = schema.Bool(title=_(u'Show comments'), 
                                                 required=True, 
                                                 default=True)
    maxComments = schema.Int(title=_(u'Number of recent comments to display '),
                       required=True,
                       default=5)    
    

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(ISimpleBlogPortlet)    
    
    def __init__(self, maxResults=5, showRecent=True, showCategories=True, showCalendar=True, showComments=True, maxComments=5):
        self.maxResults = maxResults
        self.showCategories = showCategories
        self.showRecent = showRecent
        self.showCalendar = showCalendar
        self.showComments = showComments
        self.maxComments = maxComments

    @property
    def title(self):
        return _(u"Blog Portlet")
    


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('simpleblogportlet.pt')
    updated = False

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.updated = False    
 
    def getBlog(self):
        """Return the current blog, or None when not in blog context.
        """
        for obj in aq_chain(aq_inner(self.context)):
            if ISiteRoot.providedBy(obj):
                break
            if IBlog.providedBy(obj):
                return obj

        return None
    
    @property
    def available(self):
        if self.context.isTemporary() or self.context.checkCreationFlag():
            return # we are in the factory

        mt=getToolByName(self.context, "portal_membership")
        return mt.checkPermission(VIEW_PORTLET_PERMISSION, self.context)
    
    def update(self):
        """Set all information."""

        if self.updated:
            return
        self.updated = True
        
        self.showRecent = self.data.showRecent
        self.showCategories = self.data.showCategories
        self.showCalendar = self.data.showCalendar
        self.maxResults = self.data.maxResults
        self.showComments = self.data.showComments
        self.maxComments = self.data.maxComments
        
        context = aq_inner(self.context)
        #self.calendar = getToolByName(context, 'portal_calendar')
        self.calendar = getToolByName(context, 'simpleblog_tool') # inherits from the calendar tool
        self._ts = getToolByName(context, 'translation_service')
        self.url_quote_plus = url_quote_plus

        self.now = localtime()
        self.yearmonth = yearmonth = self.getYearAndMonthToDisplay()
        self.year = year = yearmonth[0]
        self.month = month = yearmonth[1]

        self.showPrevMonth = yearmonth > (self.now[0]-1, self.now[1])
        self.showNextMonth = yearmonth < (self.now[0]+1, self.now[1])

        self.prevMonthYear, self.prevMonthMonth = self.getPreviousMonth(year, month)
        self.nextMonthYear, self.nextMonthMonth = self.getNextMonth(year, month)

        self.monthName = PLMF(self._ts.month_msgid(month),
                              default=self._ts.month_english(month))

        
    def getStartpointForSearch(self):
        bt=getToolByName(self.context, "simpleblog_tool")
        
        return bt.getStartpointForSearch(aq_inner(self.context))

    @memoize
    def collectEntries(self, startpoint):
        entries=getToolByName(self.context, "simpleblog_tool").collectEntries(startpoint, maxResults = self.data.maxResults)
        # now make sure there aren't doubles (e.g. cross posts)
        uids = []
        res = []
        for e in entries:
            if e.UID() not in uids:
                res.append(e)
                uids.append(e.UID())
        return res

    def getAvailableCategories(self, startpoint):
        return getToolByName(self.context, "simpleblog_tool").getAvailableCategories(self.context, startpoint)
    
    def getSortedKeys(self, cats):
        return getToolByName(self.context, "simpleblog_tool").getSortedKeys(cats)
    
    def more_recent_link(self):
        return '%s/SimpleBlogFullSearch' % self.context.absolute_url() 
    
    def cat_search_link(self, cat):
        return '%s/SimpleBlogCatSearch?category=%s' % (self.context.absolute_url() ,  cat)

    def getComments(self):
        fpPath='/'.join(self.getStartpointForSearch().getPhysicalPath())
        results=getToolByName(self, 'portal_catalog').searchResults(
                                   path=fpPath
                                   , meta_type='Discussion Item'
                                   , sort_on='created'
                                   , sort_order='reverse')[:self.maxComments]        
        return results

    def more_comments_link(self):
        # ${startpoint/absolute_url}/search?path=${fpPath}&amp;meta_type=Discussion+Item&amp;sort_on=created&amp;sort_order=reverse;">        
        fpPath='/'.join(self.getStartpointForSearch().getPhysicalPath())
        startpoint = self.getStartpointForSearch().absolute_url()
        return startpoint + "/search?path="+ fpPath + "&portal_type%3Alist=Discussion%20Item&sort_on=created&sort_order=reverse"

    
    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        weeks = self.calendar.getEventsForCalendar(context, month, year)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date+[self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)

        return weeks

    def getEventString(self, event):
        start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
        end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
        title = safe_unicode(event['title']) or u'event'

        if start and end:
            eventstring = "%s-%s %s" % (start, end, title)
        elif start: # can assume not event['end']
            eventstring = "%s - %s" % (start, title)
        elif event['end']: # can assume not event['start']
            eventstring = "%s - %s" % (title, end)
        else: # can assume not event['start'] and not event['end']
            eventstring = title

        return eventstring

    def getYearAndMonthToDisplay(self):
        session = None
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if self.calendar.getUseSession():
            session = request.get('SESSION', None)
            if session:
                if not year:
                    year = session.get('calendar_year', None)
                if not month:
                    month = session.get('calendar_month', None)

        # Last resort to today
        if not year:
            year = self.now[0]
        if not month:
            month = self.now[1]

        year, month = int(year), int(month)

        # Store the results in the session for next time
        if session:
            session.set('calendar_year', year)
            session.set('calendar_month', month)

        # Finally return the results
        return year, month

    def getPreviousMonth(self, year, month):
        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1
        return (year, month)

    def getNextMonth(self, year, month):
        if month==12:
            month, year = 1, year + 1
        else:
            month+=1
        return (year, month)

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""
        weekdays = []
        # list of ordered weekdays as numbers
        for day in self.calendar.getDayNumbers():
            weekdays.append(PLMF(self._ts.day_msgid(day, format='s'),
                                 default=self._ts.weekday_english(day, format='a')))

        return weekdays

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """
        return self.now[2]==day and self.now[1]==self.month and \
               self.now[0]==self.year

    def getReviewStateString(self):
        states = self.calendar.getCalendarStates()
        return ''.join(map(lambda x : 'review_state=%s&amp;' % self.url_quote_plus(x), states))

    def getQueryString(self):
        request = self.request
        query_string = request.get('orig_query',
                                   request.get('QUERY_STRING', None))
        if len(query_string) == 0:
            query_string = ''
        else:
            query_string = '%s&amp;' % query_string
        return query_string
    
    
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISimpleBlogPortlet)
    label = _(u"Add Blog Portlet")
    description = _(u"This portlet displays recent plog posts within the current blog or in the context of an entire folder structure.")
    
    def create(self, data):
        return Assignment(showRecent=data.get('showRecent', True),
                                    showCalendar=data.get('showCalendar',True),
                                    maxResults=data.get('maxResults',True),
                                    showCategories=data.get('showCategories', True),
                                    maxComments=data.get('maxComments',True),
                                    showComments=data.get('showComments', True)
                                    )

class EditForm(base.EditForm):
    form_fields = form.Fields(ISimpleBlogPortlet)
    label = _(u"Edit Blog Portlet")
    description = _(u"This portlet displays recent plog posts within the current blog or in the context of an entire folder structure.")