from Products.CMFCore.utils import UniqueObject 
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.CMFCore import permissions
import zLOG,os
from Products.CMFCore.utils import getToolByName
import re
import calendar
calendar.setfirstweekday(6) #start day  Mon(0)-Sun(6)
from DateTime import DateTime
from Products.CMFPlone.CalendarTool import CalendarTool
from Products.CMFCalendar.interfaces import ICalendarTool
from zope.interface import implements
from plone.app.portlets.utils import assignment_mapping_from_key
from Products.SimpleBlog.browser import simpleblogportlet
from Acquisition import aq_inner


class SimpleBlogManager(UniqueObject, SimpleItem,PropertyManager, CalendarTool): 
    """ This tool provides some functions for SimpleBlog objects """ 
    id = 'simpleblog_tool' 
    meta_type= 'SimpleBlog manager' 
    plone_tool = 1
        
    manage_options=PropertyManager.manage_options
    implements(ICalendarTool)
    
    security = ClassSecurityInfo()
    calendar_types=['BlogEntry']
    calendar_states = ('published',)
    
    def __init__(self):
        self.manage_addProperty('publishedState', 'published', 'string')
        self.manage_addProperty('globalCategories', '', 'lines')
        self.manage_addProperty('createPortletOnBlogCreation', 1,'boolean')
        self.manage_addProperty('showRecent', 1,'boolean')
        self.manage_addProperty('showCategories', 1,'boolean')
        self.manage_addProperty('showComments', 1,'boolean')
        self.manage_addProperty('showCalendar', 1,'boolean')
        self.manage_addProperty('allowAnonymousViewByline', 1,'boolean')

    security.declarePublic('idFromTitle')
    def idFromTitle(self, title):
        id = re.sub('[^A-Za-z0-9_]', '', re.sub(' ', '_', title)).lower()
        return id        
    
    def _getState(self):
        try:
            return self.publishedState
        except:
            return 'published'

    def _getGlobalCategories(self):
        try:
            cats = self.globalCategories
            ret=[]
            for c in cats:
                if c!='':
                    ret.append(c)
            return ret
        except:
            return []
        
    def _getCreatePortletOnBlogCreation(self):
        try:
            return self.createPortletOnBlogCreation
        except:
            return 1

    def _getAllowAnonymousViewByline(self):
        try:
            return self.allowAnonymousViewByline
        except:
            return 1        

    def _getShowRecent(self):
        try:
            return self.showRecent
        except:
            return 1
        
    def _getShowCalendar(self):
        try:
            return self.showCalendar
        except:
            return 1
        
    def _getShowCategories(self):
        try:
            return self.showCategories
        except:
            return 1
        
    def _getShowComments(self):
        try:
            return self.showComments
        except:
            return 1
        
        
    security.declareProtected(permissions.ManagePortal,'setProperties')        
    def setProperties(self, publishedState='published', 
                                    createPortletOnBlogCreation=None, 
                                    globalCategories='', 
                                    allowAnonymousViewByline=None,
                                    showRecent=None,
                                    showCalendar=None,
                                    showCategories=None,
                                    showComments=None):

        self.publishedState = publishedState
        
        if createPortletOnBlogCreation==1 or createPortletOnBlogCreation=='on':
            self.createPortletOnBlogCreation=1
        else:
            self.createPortletOnBlogCreation=0
            
        if allowAnonymousViewByline==1 or allowAnonymousViewByline=='on':
            self.allowAnonymousViewByline=1
        else:
            self.allowAnonymousViewByline=0

        if showRecent==1 or showRecent=='on':
            self.showRecent=1
        else:
            self.showRecent=0
            
        if showCategories==1 or showCategories=='on':
            self.showCategories=1
        else:
            self.showCategories=0
            
        if showComments==1 or showComments=='on':
            self.showComments=1
        else:
            self.showComments=0

        if showCalendar==1 or showCalendar=='on':
            self.showCalendar=1
        else:
            self.showCalendar=0
            
        value=''
        if globalCategories<>'':
            value =  globalCategories.split('\n')
            value = [v.strip() for v in value if v.strip()]
            value = filter(None, value)

        self.globalCategories=value
    
    security.declarePublic('getPublishedState')
    def getPublishedState(self):
        return self._getState()
    
    security.declarePublic('getFrontPage')
    def getFrontPage(self, context):
        """
        returns the frontpage (Blog object) when viewing an Entry
        """
        if context.portal_type!='Blog':
            portal = context.portal_url.getPortalObject()
            if context!=portal:
                parent=context.aq_parent
            else:
                parent=context
            found=0
            while parent!=portal and context.portal_type!='Blog':
                if parent.portal_type=='Blog':
                    found=1
                    break
                parent=parent.aq_parent
            
            if found==1:
                return parent
            else:
                return None
        else:
            return context
    security.declarePublic('getStartpointForSearch')
    def getStartpointForSearch(self, context):
        """
        When in the context of a blog, return the blog
        Outside the context of a blog, return context or if context isn't
        folderish, it's parent container
        """
        plone_utils = getToolByName(context, 'plone_utils')
        
        startpoint = self.getFrontPage(context)
        if not startpoint:
            # we weren't in the context of a blog
            if plone_utils.isStructuralFolder(context):
                return context
            else:
                return context.aq_parent
        else:
            return startpoint
     
    security.declarePublic('getAvailableCategories')
    def getAvailableCategories(self, context, startpoint=None):
        """
        returns a dict of all the available categories with the number of posts inside
        """
        # get all EntryFolders
        # first get the starting point in case we are inside a Blog section
        # if we are higher in the tree than any Blog then we will end up in the portalobject itself
        # in that case we just search for categories starting in context.

        if not startpoint:
            startpoint = self.getStartpoint(context, fromHere=0)

        # now we have the starting point for our search
        
        result = startpoint.portal_catalog.searchResults(meta_type=['BlogFolder', 'Blog'], path={'query':self.getObjectPath(startpoint),'level':0})
        
        # now fetch all the available categories
        categories=[]
        for o in result:
            obj=o.getObject()
            cats = obj.getCategories()
            for c in cats:
                if not c in categories:
                    categories.append(c)
        
        # add the global categories
        for c in self.getGlobalCategories():
            if not c in categories:
                categories.append(c)
        
        # now we have a list of unique categories available from startpoint and deeper in tree
        # next step is to count the number of entries for each category
        rescats={}
        for c in categories:
            result = startpoint.portal_catalog.searchResults(review_state=self._getState(), meta_type='BlogEntry', EntryCategory=c,  path={'query':self.getObjectPath(startpoint),'level':0})
            rescats[c]=len(result)
        return rescats        
    
    security.declarePublic('getSortedKeys')
    def getSortedKeys(self, dict):
        keys = dict.keys()
        keys.sort()
        return keys
    
    security.declarePublic('getGlobalCategories')
    def getGlobalCategories(self):
        return self._getGlobalCategories()
    
    security.declarePublic('getStartpoint')
    def getStartpoint(self, context, fromHere=0):
        if context.portal_type!='Blog' and fromHere==0:
            portal = context.portal_url.getPortalObject()
            if context!=portal:
                parent=context.aq_parent
            else:
                parent=context
            found=0
            while parent!=portal and context.portal_type!='Blog':
                if parent.portal_type=='Blog':
                    found=1
                    break
                parent=parent.aq_parent
            
            if found==1:
                startpoint=parent
            else:
                if context.isPrincipiaFolderish:
                    startpoint=context
                else:
                    startpoint=context.aq_parent
        else:
            startpoint=context

        return startpoint
    
    security.declarePublic('searchForEntries')
    def searchForEntries(self, context, category=None, maxResults=None, fromHere=0, filterState=1, **kwargs):
        # set maxResults=0 for all the results,
        # leave it to None to get the max from the properties
        # set fromHere=1 to search from the current location. Is used for BlogFolders
        
        # first, get the context right
        # when inside a Blog: search for the frontpage
        # when outside a Blog: use context (or its container)
        
        #filterState controls whether you want to return only published entries
            
        startpoint = self.getStartpoint(context, fromHere)
        # now we have the starting point for our search
        
        query=kwargs

        publishedState = self._getState()
        
        if category!=None:
            query['EntryCategory']=category

        query['getAlwaysOnTop']=1
        
        if filterState:
            query['review_state']=publishedState            

            
        resultsTop = startpoint.portal_catalog.searchResults(query, meta_type='BlogEntry', path={'query':self.getObjectPath(startpoint),'level':0}, sort_order='reverse', sort_on='effective')
        
        query['getAlwaysOnTop']=0
        resultsNoTop = startpoint.portal_catalog.searchResults(query, meta_type='BlogEntry', path={'query':self.getObjectPath(startpoint),'level':0}, sort_order='reverse', sort_on='effective')
        
        results = resultsTop + resultsNoTop

        if maxResults==0 or maxResults==None:
            return results
        else:
            return results[:maxResults]    


    security.declarePublic('searchForEntries')
    def collectEntries(self, context, category=None, maxResults=None,  filterState=1,  **kwargs):
        # first get all the blogs
        query = {'meta_type':'Blog',
                       'path':{'query':self.getObjectPath(context),'level':0}
                    } # used meta_type because for some reason, syndication objects also show up.
        blogs = [b.getObject() for b in self.portal_catalog.searchResults(query)]
        
        onTop=[]
        atBottom=[]
        # now collect all the entries
        for blog in blogs:
            tmpTop, tmpBottom = blog.getEntries(category=category, maxResults=0, filterState = filterState, sort=0, **kwargs)
            onTop = onTop+tmpTop
            atBottom = atBottom+tmpBottom

        #sort
        onTop.sort((lambda x,y:cmp(y.effective(), x.effective())))
        atBottom.sort((lambda x,y:cmp(y.effective(), x.effective())))

        results = onTop+atBottom
        
        if maxResults==0 or maxResults == None:
            return results
        else:
            return results[:maxResults]      
        
        
    security.declarePublic('searchForDay')
    def searchForDay(self, context, date):
        startpoint = self.getStartpoint(context, fromHere=0)
        # now we have the starting point for our search
        
        query={'start': DateTime(date).earliestTime(), 'start_usage': 'range:min', 
                    'end': DateTime(date).latestTime(), 'end_usage':'range:max'}
        query['getAlwaysOnTop']=1
        resultsTop = startpoint.portal_catalog.searchResults(query, 
                                                             review_state=self._getState(), 
                                                             meta_type='BlogEntry', 
                                                             path={'query':self.getObjectPath(startpoint),'level':0}, 
                                                             sort_order='reverse', sort_on='effective')
        
        
        query['getAlwaysOnTop']=0
        resultsNoTop = startpoint.portal_catalog.searchResults(query, 
                                                             review_state=self._getState(), 
                                                             meta_type='BlogEntry', 
                                                             path={'query':self.getObjectPath(startpoint),'level':0}, 
                                                             sort_order='reverse', sort_on='effective')
        
        results = resultsTop + resultsNoTop
        return results
   
    security.declarePublic('getUnpublishedEntries')
    def getUnpublishedEntries(self, blog):
        states = self. getEntryWorkflowStates(blog)
        pubstate = self.getPublishedState()
        states = [s for s in states if s!=pubstate]
        query={'review_state':states}
        entries = self.searchForEntries(blog, filterState=0, maxResults=0, fromHere=1, **query)
        return entries
   
    security.declarePublic('blogHasEntries')
    def blogHasEntries(self, context, fromHere=0):
        """
        returns if a blog has entries, either published or not published. 
        this function is used to display a message in the simpleblog(folder)_view when
        there are entries but none of them published
        """
        startpoint = self.getStartpoint(context, fromHere=0)
        
        # get all entries, doesn't matter what state they're in
        results = startpoint.portal_catalog.searchResults(meta_type='BlogEntry', path={'query':self.getObjectPath(startpoint),'level':0})        
        
        if results:
            return True
        else:
            return False
    
    security.declarePublic('getEntryDate')
    def getEntryDate(self, context):
        if context.EffectiveDate()=='None':
            return context.modification_date.aCommon()
        else:
            return context.EffectiveDate()

    security.declarePublic('getCreatePortletOnBlogCreation')
    def getCreatePortletOnBlogCreation(self):
        return self._getCreatePortletOnBlogCreation()

    security.declarePublic('getAllowAnonymousViewByline')
    def getAllowAnonymousViewByline(self):
        return self._getAllowAnonymousViewByline()

    security.declarePublic('getShowRecent')
    def getShowRecent(self):
        return self._getShowRecent()
    
    security.declarePublic('getShowCategories')
    def getShowCategories(self):
        return self._getShowCategories()

    security.declarePublic('getShowCalendar')
    def getShowCalendar(self):
        return self._getShowCalendar()

    security.declarePublic('getShowComments')
    def getShowComments(self):
        return self._getShowComments()
    
    security.declareProtected(permissions.ManagePortal,'getAllWorkflowStates')
    def getAllWorkflowStates(self, context):
        lst=[]
        for wf in context.portal_workflow.listWorkflows():
            states = context.portal_workflow.getWorkflowById(wf).states
            for s in states.keys():
                if not states[s].id in lst:
                    lst.append(states[s].id)
        return lst
    
    security.declareProtected(permissions.ManagePortal,'getEntryWorkflowStates')
    def getEntryWorkflowStates(self, context):
        chain = context.portal_workflow.getChainForPortalType('BlogEntry', 0)
        lst=[]
        for wf in chain:
            states = context.portal_workflow.getWorkflowById(wf).states
            for s in states.keys():
                if not states[s].id in lst:
                    lst.append(states[s].id)
        
        return lst

    # return object's url relative to the portal
    def getObjectPath(self, object):
        return os.path.join(*object.getPhysicalPath()).replace('\\', '/')
    security.declarePublic('getEventsForCalendar')
    def getEventsForCalendar(self, here, month='1', year='2002'):
        """ recreates a sequence of weeks, by days each day is a mapping.
            {'day': #, 'url': None}
        """
        year = int(year)
        month = int(month)
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]
        daysByWeek = self._getCalendar().monthcalendar(year, month)
        weeks = []

        events = self.catalog_getevents(year, month, here)

        for week in daysByWeek:
            days = []
            for day in week:
                if events.has_key(day):
                    days.append(events[day])
                else:
                    days.append({'day': day, 'event': 0, 'eventslist':[]})

            weeks.append(days)

        return weeks
    
    def catalog_getevents(self, year, month, here):
        """ given a year and month return a list of days that have events 
        """
        # XXX: this method violates the rules for tools/utilities:
        # it depends on a non-utility tool
        year = int(year)
        month = int(month)
        last_day = self._getCalendar().monthrange(year, month)[1]
        first_date = self.getBeginAndEndTimes(1, month, year)[0]
        last_date = self.getBeginAndEndTimes(last_day, month, year)[1]

        ctool = getToolByName(self, 'portal_catalog')
        
        # get the starting point for our search. This is where we depart from the standard catalog_tool:
        startpoint = self.getStartpoint(here, fromHere=0)
                
        query = ctool(
                        portal_type=self.getCalendarTypes(),
                        review_state=self._getState(),
                        start={'query': last_date, 'range': 'max'},
                        end={'query': first_date, 'range': 'min'},
                        path={'query':self.getObjectPath(startpoint),'level':0},
                        sort_on='start' )

        # compile a list of the days that have events
        eventDays={}
        for daynumber in range(1, 32): # 1 to 31
            eventDays[daynumber] = {'eventslist': [],
                                    'event': 0,
                                    'day': daynumber}
        includedevents = []
        for result in query:
            if result.getRID() in includedevents:
                break
            else:
                includedevents.append(result.getRID())
            event={}
            # we need to deal with events that end next month
            if  result.end.month() != month:
                # doesn't work for events that last ~12 months
                # fix it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event['end'] = None
            else:
                eventEndDay = result.end.day()
                event['end'] = result.end.Time()
            # and events that started last month
            if result.start.month() != month:  # same as above (12 month thing)
                eventStartDay = 1
                event['start'] = None
            else:
                eventStartDay = result.start.day()
                event['start'] = result.start.Time()

            event['title'] = result.Title or result.getId

            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay+1)
                eventDays[eventStartDay]['eventslist'].append(
                        {'end': None,
                         'start': result.start.Time(),
                         'title': event['title']} )
                eventDays[eventStartDay]['event'] = 1

                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]['eventslist'].append(
                        {'end': None,
                         'start': None,
                         'title': event['title']} )
                    eventDays[eventday]['event'] = 1

                if result.end == result.end.earliestTime():
                    last_day_data = eventDays[allEventDays[-2]]
                    last_days_event = last_day_data['eventslist'][-1]
                    last_days_event['end'] = (result.end-1).latestTime().Time()
                else:
                    eventDays[eventEndDay]['eventslist'].append( 
                        { 'end': result.end.Time()
                        , 'start': None, 'title': event['title']} )
                    eventDays[eventEndDay]['event'] = 1
            else:
                eventDays[eventStartDay]['eventslist'].append(event)
                eventDays[eventStartDay]['event'] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays
    
    security.declareProtected(permissions.ManagePortal,'migrateBlogPortlets')
    def migrateBlogPortlets(self):
        # first find all the blogs
        pc = getToolByName(self, 'portal_catalog')
        blogs = pc.searchResults(portal_type=('Blog',))
        
        for blog in blogs:
            obj = blog.getObject()
            print "Scanning for portlets in blog " + obj.absolute_url()
            right_portlets = getattr(aq_inner(obj), 'right_slots', [])
            left_portlets = getattr(aq_inner(obj), 'left_slots', [])
            rportlets = [(p, u"plone.rightcolumn") for p in right_portlets]
            lportlets = [(p, u"plone.leftcolumn") for p in left_portlets]
            portlets = rportlets + lportlets
            if portlets: print "Start migrating blog " + obj.absolute_url()
            index=0 # used for unique mapping keys in combi with uids
            
            # reset, we will add other (old) portlets that aren't ours so we 
            # can later restore them
            right_portlets=[]
            left_portlets = []
            rewrite_right_slots=False
            rewrite_left_slots=False

            # now process the portlets
            for portlet, position in portlets:
                print "     Portlet " + portlet + ", position: " + position
                portlet_mapping = assignment_mapping_from_key(
                   context=obj,
                   manager_name=position,
                   category="context",
                   key="/".join(obj.getPhysicalPath()))
                
                # see if the portlet is ours
                if portlet == 'here/portlet_simpleblog/macros/portletBlogFull_local':
                    showComments = False # this was always a separate portlet
                    showRecent = True
                    showCalendar = True
                    showCategories = True
                elif portlet == 'here/portlet_simpleblog/macros/portletBlogRecent_local':
                    showComments = False # this was always a separate portlet
                    showRecent = True
                    showCalendar = False
                    showCategories = False
                elif portlet == 'here/portlet_simpleblog/macros/portlet':
                    showComments = False # this was always a separate portlet
                    showRecent = True
                    showCalendar = True
                    showCategories = True
                elif portlet == 'here/portlet_simpleblog/macros/portlet-recent':
                    showComments = False # this was always a separate portlet
                    showRecent = True
                    showCalendar = False
                    showCategories = False
                elif portlet == 'here/portlet_simpleblog/macros/portlet-comments':
                    showComments = True
                    showRecent = False
                    showCalendar = False
                    showCategories = False
                else:
                    # nope.. it's another one, restore it later
                    if position==u"plone.rightcolumn":
                        right_portlets.append(portlet)
                        rewrite_right_slots=True
                    else:
                        left_portlets.append(portlet)
                        rewrite_left_slots=True
                    continue # it's not a blog portlet, 
                
                # ok, we have set the params for the new portlet, let's add it
                index=index+1
                print "          showComments: " + str(showComments)
                print "          showRecent: " + str(showRecent)
                print "          showCategories: " + str(showCategories)
                print "          showCalendar: " + str(showCalendar)

                portlet_mapping[obj.UID() + str(index)] = simpleblogportlet.Assignment(showCategories = showCategories,
                                                                                                   showCalendar = showCalendar,
                                                                                                   showRecent = showRecent,
                                                                                                   showComments = showComments)
                # and hop.. up to the next one
            
            # when needed, restore the other portlets
            if rewrite_right_slots:
                setattr(obj, 'right_slots', right_portlets)
            if rewrite_left_slots:
                setattr(obj, 'left_slots', right_portlets)
                
            obj.reindexObject()  
            if portlets: print "Finished migrating blog " + obj.absolute_url()
            
        print "Finished them all"
        
        
InitializeClass(SimpleBlogManager)