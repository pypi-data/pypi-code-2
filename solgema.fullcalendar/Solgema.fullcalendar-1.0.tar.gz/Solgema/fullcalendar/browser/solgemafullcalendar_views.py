from urllib import unquote
from OFS import CopySupport
from Acquisition import aq_base, aq_inner, aq_parent
from zope.interface import implements, Interface
from Products.Five import BrowserView
from zope.component import getMultiAdapter, queryMultiAdapter, getAdapters, queryUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils as CMFPloneUtils
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
from DateTime import DateTime
import datetime
try:
    import json
except:
    import simplejson as json
from AccessControl import getSecurityManager
from Solgema.fullcalendar.config import _
plMF = MessageFactory('plone')
PLMF = MessageFactory('plonelocales')
ATMF = MessageFactory('atcontenttypes')
DTMF = MessageFactory('collective.z3cform.datetimewidget')
from Solgema.fullcalendar.interfaces import *

def getCopyObjectsUID(REQUEST):
    if REQUEST is not None and REQUEST.has_key('__cp'):
        cp = REQUEST['__cp']
    else:
        return []

    op, mdatas = CopySupport._cb_decode(cp)
    return {'op':op, 'url': ['/'.join(a) for a in mdatas][0]}

def listQueryTopicCriteria(topic):
    calendar = ISolgemaFullcalendarProperties(aq_inner(topic), None)
    li = []
    for criteria in topic.listCriteria():
        if criteria.meta_type=='ATPortalTypeCriterion' and len(criteria.getCriteriaItems()[0][1])>1:
            li.append(criteria)
        if criteria.meta_type in ['ATSelectionCriterion', 'ATListCriterion'] and len(criteria.getCriteriaItems()[0][1]['query'])>1:
            li.append(criteria)
    if hasattr(calendar, 'availableCriterias') and getattr(calendar, 'availableCriterias', None) != None:
        li = [a for a in li if a.Field() in calendar.availableCriterias]
    return li

def getTopic(context, request):
    if not ISolgemaFullcalendarMarker.providedBy(context):
        utils = getToolByName(context, 'plone_utils')
        page = utils.getDefaultPage(context, request)
        pageItem = page and getattr(context, page) or None
        if ISolgemaFullcalendarMarker.providedBy(pageItem):
            return pageItem
        portal = getToolByName(context, 'portal_url').getPortalObject()
        referer = unquote(request.get('last_referer', request.get('HTTP_REFERER')))
        if referer.find('?')!=-1:
            referer = referer[:referer.index('?')]
        if referer[-5:] == '/view':
            referer = referer[:-5]
        if referer[-1:] == '/':
            referer = referer[:-1]
        portal_url = portal.absolute_url()
        topic_url = referer.replace(portal_url, '')
        topic = portal.restrictedTraverse('/'+portal.id+topic_url)
        if utils.getDefaultPage(topic, request):
            page = utils.getDefaultPage(topic, request)
            topic_url = topic_url+'/'+page
            topic = getattr(topic, page)
            if ISolgemaFullcalendarMarker.providedBy(topic):
                return topic
        url = '/'+portal.id+topic_url
        while not ISolgemaFullcalendarMarker.providedBy(topic):
            url = url[0:url.rindex('/')]
            try:
                topic = portal.restrictedTraverse(url)
            except:
                break
                raise str(url)
        return topic
    else:
        return context

def getCriteriaItems(context, request):
    topic = getTopic(context, request)
    utils = getToolByName(context, 'plone_utils')
    listCriteria = topic.listCriteria()
    topicCriteria = listQueryTopicCriteria(topic)
    if topicCriteria:
        selectedCriteria = request.cookies.get('sfqueryDisplay', topicCriteria[0].Field())
        criteria = [a for a in listCriteria if a.Field() == selectedCriteria]
    else:
        criteria = listCriteria
    criteria = [a for a in criteria if a.meta_type in ['ATPortalTypeCriterion', 'ATSelectionCriterion', 'ATListCriterion']]
    if not criteria:
        return False
    criteria = criteria[0]
    if criteria.meta_type=='ATPortalTypeCriterion':
        return {'name':criteria.Field(), 'values':list(criteria.getCriteriaItems()[0][1])}
    if criteria.meta_type in ['ATSelectionCriterion', 'ATListCriterion']:
        return {'name':criteria.Field(), 'values':list(criteria.getCriteriaItems()[0][1]['query'])+['',]}
    return False

def getCookieItems(request, field):
    item = request.cookies.get(field, False)
    if item:
        items = item.find('+') == -1 and item or item.split('+')
        #it seems that sometimes it's utf-8 encoded and sometimes iso-8859-1.....
        if isinstance(items, (list, tuple)):
            try:
                items = [a.decode('iso-8859-1') for a in items]
            except:
                pass
            try:
                items = [a.decode('utf-8') for a in items]
            except:
                pass
            items = [a.encode('utf-8') for a in items]
        else:
            try:
                items = items.decode('iso-8859-1')
            except:
                pass
            try:
                items = items.decode('utf-8')
            except:
                pass
            items = items.encode('utf-8')
        return items
    return False

def getColorIndex(context, request, eventPath=None, brain=None):
    colorIndex = ' colorIndex-undefined'
    criteriaItems = getCriteriaItems(context, request)
    if not criteriaItems:
        return colorIndex
    catalog = getToolByName(context, 'portal_catalog')
    if not brain:
        if not eventPath:
            raise ValueError(u'Use must provide eventPath or brain')
        brain = catalog.searchResults(path=eventPath)[0]
    selectedItems = getCookieItems(request, criteriaItems['name'])
    if not selectedItems:
        selectedItems = criteriaItems['values']
    if not isinstance(selectedItems, list):
        selectedItems = [selectedItems,]
    if criteriaItems:
        brainVal = getattr(brain, criteriaItems['name'])
        brainVal = isinstance(brainVal, (tuple, list)) and brainVal or [brainVal,]
        for val in brainVal:
            if criteriaItems['values'].count(val) != 0 and val in selectedItems:
                colorIndex = ' colorIndex-'+str(criteriaItems['values'].index(val))
                break
    return colorIndex

class SolgemaFullcalendarView(BrowserView):
    """Solgema Fullcalendar Browser view for Fullcalendar rendering"""

    implements(ISolgemaFullcalendarView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.calendar = ISolgemaFullcalendarProperties(aq_inner(context), None)

    def getCriteriaClass(self):
        anon = self.context.portal_membership.isAnonymousUser()
        listCriteria = self.context.listCriteria()
        if listCriteria[0].Field() == 'review_state' and anon:
            return ''
        return self.request.cookies.get('sfqueryDisplay', listCriteria[0].Field())

class SolgemaFullcalendarJS(BrowserView):
    """Solgema Fullcalendar Javascript variables"""

    implements(ISolgemaFullcalendarJS)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.calendar = ISolgemaFullcalendarProperties(aq_inner(context), None)
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self._ts = getToolByName(context, 'translation_service')
        self.portal_language = self.getPortalLanguage()

    def getPortalLanguage(self):
        ltool = getToolByName(self.context, 'portal_languages')
        lang = ltool.getPreferredLanguage()
        lang = lang[:2]
        return lang

    def getFirstDay(self):
        if getattr(self.calendar, 'relativeFirstDay', '') in [None, '']:
            return self.calendar.firstDay
        else:
            now = datetime.datetime.now()
            delta = datetime.timedelta(hours=int(getattr(self.calendar, 'relativeFirstDay')))
            newdate = now+delta
            return newdate.isoweekday()-1

    def getYear(self):
        if getattr(self.calendar, 'relativeFirstDay', '') in [None, '']:
            return datetime.datetime.now().year
        else:
            now = datetime.datetime.now()
            delta = datetime.timedelta(hours=int(getattr(self.calendar, 'relativeFirstDay')))
            newdate = now+delta
            return int(newdate.year)

    def getMonthNumber(self):
        if getattr(self.calendar, 'relativeFirstDay', '') in [None, '']:
            return datetime.datetime.now().month
        else:
            now = datetime.datetime.now()
            delta = datetime.timedelta(hours=int(getattr(self.calendar, 'relativeFirstDay')))
            newdate = now+delta
            return int(newdate.month)

    def getDate(self):
        if getattr(self.calendar, 'relativeFirstDay', '') in [None, '']:
            return datetime.datetime.now().day
        else:
            now = datetime.datetime.now()
            delta = datetime.timedelta(hours=int(getattr(self.calendar, 'relativeFirstDay')))
            newdate = now+delta
            return int(newdate.day)

    def getMonthsNames(self):
        return [PLMF(self._ts.month_msgid(m), default=self._ts.month_english(m)) for m in [a+1 for a in range(12)]]

    def getMonthsNamesAbbr(self):
        return [PLMF(self._ts.month_msgid(m, format='a'), default=self._ts.month_english(m, format='a')) for m in [a+1 for a in range(12)]]

    def getWeekdaysNames(self):
        return [PLMF(self._ts.day_msgid(d), default=self._ts.weekday_english(d)) for d in range(6)]

    def getWeekdaysNamesAbbr(self):
        return [PLMF(self._ts.day_msgid(d, format='a'), default=self._ts.weekday_english(d, format='a')) for d in range(6)]

    def getTodayTranslation(self):
        return DTMF('Today', 'Today')

    def getMonthTranslation(self):
        return _('Month', 'Month')

    def getWeekTranslation(self):
        return _('Week', 'Week')

    def getDayTranslation(self):
        return _('Day', 'Day')

    def getAllDayText(self):
        return _('Allday', 'all-day')

    def getAddEventText(self):
        return _('addNewEvent', 'Add New Event')

    def getEditEventText(self):
        return _('editEvent', 'Edit Event')

    def getCustomTitleFormat(self):
        if self.portal_language in ['fr']:
            return '{month: "MMMM yyyy", week: "d[ MMM][ yyyy]{ \'-\' d MMM yyyy}", day: \'dddd, d MMMM yyyy\'}'
        elif self.portal_language in ['de']:
            return '{month: \'MMMM yyyy\', week: "d[ yyyy]. MMMM{ \'-\'d.[ MMMM] yyyy}", day: \'dddd, d. MMMM yyyy\'}'
        else:
            return '{month: \'MMMM yyyy\', week: "MMM d[ yyyy]{ \'-\'[ MMM] d yyyy}", day: \'dddd, MMM d, yyyy\'}'

    def getHourFormat(self):
        if self.portal_language in ['fr', 'de', 'it']:
            return 'HH(:mm)'
        else:
            return 'h(:mm)tt'

    def getTargetFolder(self):
        target_folder = getattr(self.calendar, 'target_folder', None)
        addContext = target_folder and self.portal.restrictedTraverse('/'+self.portal.id+target_folder) or aq_parent(aq_inner(self.context))
        return addContext.absolute_url()

    def getHeaderRight(self):
        headerRight = getattr(self.calendar, 'headerRight', ['month', 'agendaWeek', 'agendaDay'])
        return ','.join(headerRight)

    def getPloneVersion(self):
        portal_migration = getToolByName(self.context, 'portal_migration')
        try:
            return portal_migration.getSoftwareVersion()
        except:
            return portal_migration.getInstanceVersion()

    def getTopicRelativeUrl(self):
        if CMFPloneUtils.isDefaultPage(self.context, self.request):
            return '/'+aq_parent(aq_inner(self.context)).absolute_url(relative=1)
        else:
            return '/'+self.context.absolute_url(relative=1)

class SolgemaFullcalendarEvents(BrowserView):
    """Solgema Fullcalendar Update browser view"""

    implements(ISolgemaFullcalendarEvents)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.copyDict = getCopyObjectsUID(request)

    def _listSFAllowedRolesAndUsersModify(self):
        user = getSecurityManager().getUser()
        effective_roles = user.getRoles()
        sm = getSecurityManager()
        if sm.calledByExecutable():
            eo = sm._context.stack[-1]
            proxy_roles = getattr(eo, '_proxy_roles', None)
            if proxy_roles is not None:
                effective_roles = proxy_roles
        result = list( effective_roles )
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
        return result

    def convertAsList(self, items):
        if isinstance(items, str):
            return [items,]
        return items

    def __call__(self, *args, **kw):
        """Render JS Initialization code"""

        response = self.request.response
        context = self.context
        query = self.context.buildQuery()
        response.setHeader('Content-Type', 'application/x-javascript')
        topicCriteria = listQueryTopicCriteria(self.context)
        args = {}

        if 'Type' in query.keys():
            items = getCookieItems(self.request, 'Type')
            if items:
                args['Type'] = items
            else:
                args['Type'] = query['Type']
        filters = []
        #reinit cookies if criterions are no more there
        for criteria in self.context.listCriteria():
            if criteria not in listQueryTopicCriteria(self.context):
                response.expireCookie(criteria.Field())
        if self.request.cookies.get('sfqueryDisplay', None) not in [a.Field() for a in topicCriteria]:
            response.expireCookie('sfqueryDisplay')

        for criteria in self.context.listCriteria():
            if criteria.meta_type not in ['ATSelectionCriterion', 'ATListCriterion', 'ATSortCriterion', 'ATPortalTypeCriterion'] and criteria.Field():
                args[criteria.Field()] = query[criteria.Field()]
            elif criteria.meta_type in ['ATSelectionCriterion', 'ATListCriterion']:
                items = getCookieItems(self.request, criteria.Field())
                if items and criteria in topicCriteria:
                    if 'undefined' in items:
                        filters.append({'name':criteria.Field(), 'values':items})
                    else:
                        args[criteria.Field()] = items
                else:
                    args[criteria.Field()] = query[criteria.Field()]
        args['start'] = {'query': DateTime(self.request.get('end')), 'range':'max'}
        args['end'] = {'query': DateTime(self.request.get('start')), 'range':'min'}
        catalog = getToolByName(context, 'portal_catalog')
        editargs = args.copy()
        editargs['SFAllowedRolesAndUsersModify'] = self._listSFAllowedRolesAndUsersModify()
        brains = catalog.searchResults(**args)
        editpaths = [a.getURL() for a in catalog.searchResults(**editargs)]
        for filt in filters:
            if isinstance(filt['values'], str):
                brains = [ a for a in brains if not getattr(a, filt['name']) ]
            else:
                brains = [ a for a in brains if not getattr(a, filt['name']) or len([b for b in self.convertAsList(getattr(a, filt['name'])) if b in filt['values']])>0 ]
                
        result = []
        member = self.context.portal_membership.getAuthenticatedMember()
        memberid = member.id
        criteriaItems = getCriteriaItems(self.context, self.request)
        for brain in brains:
            if memberid in brain.Creator:
                editable = True
            else:
                editable = False
            if brain.getURL() in editpaths:
                editable = True
            else:
                editable = False
            if brain.end - brain.start > 1.0:
                allday = True
            else:
                allday = False
            if getattr(brain, 'SFAllDay', None) in [False,True]:
                allday = brain.SFAllDay
            copycut = ''
            if self.copyDict and brain.getPath() == self.copyDict['url']:
                copycut = self.copyDict['op'] == 1 and ' event_cutted' or ' event_copied'
            typeClass = ' type-'+brain.portal_type
            colorIndex = getColorIndex(self.context, self.request, brain=brain)
            result.append({"id": "UID_%s" % (brain.UID), 
                           "title": brain.Title, 
                           "description": brain.Description,
                           "start": brain.start.rfc822(),
                           "end": brain.end.rfc822(),
                           "url": brain.getURL(),
                           "editable": editable,
                           "allDay": allday, 
                           "className": "contextualContentMenuEnabled state-" + str(brain.review_state) + (editable and " editable" or "")+copycut+typeClass+colorIndex})
        return json.dumps(result, sort_keys=True)
