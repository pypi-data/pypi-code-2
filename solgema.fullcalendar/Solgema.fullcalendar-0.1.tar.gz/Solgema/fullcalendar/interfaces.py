import itertools
from Products.ZCTextIndex.ParseTree import ParseError
from zope.interface import Interface, Attribute
from zope.interface import implements, classProvides
from zope.schema.interfaces import ISource, IContextSourceBinder
from plone.theme.interfaces import IDefaultPloneLayer
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope import interface, schema
from Solgema.fullcalendar.config import _
from Products.ATContentTypes import ATCTMessageFactory as ATMF
from Products.Archetypes import PloneMessageFactory as PMMF
from zope.i18nmessageid import MessageFactory
PMF = MessageFactory('plone')
import datetime
from zope.component.interface import provideInterface
from zope.component.tests import ITestType

from plone.app.vocabularies.catalog import SearchableTextSource, SearchableTextSourceBinder

from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem
from zope.app.publisher.interfaces.browser import IMenuItemType
from zope.viewlet.interfaces import IViewletManager

from zope.contentprovider.interfaces import IContentProvider
from Products.ATContentTypes.interface import IATFolder

class IPersistentOptions( Interface ):
    """
    a base interface that our persistent option annotation settings,
    can adapt to. specific schemas that want to have context stored
    annotation values should subclass from this interface, so they
    use adapation to get access to persistent settings. for example,
    settings = IMySettings(context)
    """

class ISolgemaFullcalendarLayer(IDefaultPloneLayer):
    """Solgema Fullcalendar layer""" 

class ISolgemaFullcalendarView(Interface):
    """Solgema Fullcalendar View interface"""

class ISolgemaFullcalendarJS(ISolgemaFullcalendarView):
    """Solgema Fullcalendar View interface for JS Vars"""

    def getCalendar(self):
        """return the context and mark it with ISolgemaFullcalendarProperties so calendar data can be stored"""

    def getPortalLanguage(self):
        """get portal language"""

    def getMonthsNames(self):
        """get name of moths"""

    def getMonthsNamesAbbr(self):
        """get name of moths abbr"""

    def getWeekdaysNames(self):
        """get name of days"""

    def getWeekdaysNamesAbbr(self):
        """get name of days abbr"""

    def getTodayTranslation(self):
        """get translation for today"""

    def getMonthTranslation(self):
        """get translation for month"""

    def getWeekTranslation(self):
        """get translation for week"""

    def getDayTranslation(self):
        """get translation for day"""

    def getAllDayText(self):
        """get translation for all-day"""

    def getCustomTitleFormat(self):
        """get format to display dates in calendar header"""

    def userCanEdit(self):
        """return if user can edit calendar"""

class CustomSearchableTextSource(SearchableTextSource):
    implements(ISource)
    classProvides(IContextSourceBinder)

    def __init__(self, context, base_query={}, default_query=None):
        super(CustomSearchableTextSource, self).__init__(context, base_query=base_query, default_query=default_query)
        self.vocabulary = SimpleVocabulary([SimpleTerm(a, a, a) for a in self.baseTerms()])

    def baseTerms(self):
        query = self.base_query.copy()
        try:
            results = (x.getPath()[len(self.portal_path):] for x in self.catalog(**query))
        except ParseError:
            return []

        if query.has_key('path'):
            path = query['path']['query'][len(self.portal_path):]
            if path != '':
                return itertools.chain((path,), results)
        return results

    def search(self, query_string):
        results = super(CustomSearchableTextSource, self).search(query_string)
        return SimpleVocabulary([SimpleTerm(a, a, a) for a in results])

    def __contains__(self, value):
        return self.vocabulary.__contains__(value)

    def __iter__(self):
        return self.vocabulary.__iter__()

    def getTerm(self, value): 
        return self.vocabulary.getTerm(value)


    def getTermByToken(self, token): 
        return self.vocabulary.getTermByToken(token)
    

class CustomSearchableTextSourceBinder(SearchableTextSourceBinder):
    implements(IContextSourceBinder)
    def __call__(self, context):
        return CustomSearchableTextSource(context, base_query=self.query.copy(),
                                    default_query=self.default_query)

class ISolgemaFullcalendarProperties(Interface):
    """An interface for specific calendar content stored in the object"""

    slotMinutes = schema.Int( title = _(u"label_slotMinutes"),
                                  required = True,
                                  description = _(u"help_slotMinutes"),
                                  default = 30 )

    allDaySlot = schema.Bool( title=_(u"label_allDaySlot"), default=True)

    defaultCalendarView = schema.Choice( title = _(u"label_defaultCalendarView"),
                                  required = True,
                                  description = _(u"help_defaultCalendarView"),
                                  source = "solgemafullcalendar.availableViews",
                                  default = 'agendaWeek' )

    headerRight = schema.List( title = _(u"label_headerRight"),
                                  description = _(u"help_headerRight"),
                                  value_type = schema.Choice( title = _(u"label_headerRight"), source = "solgemafullcalendar.availableViews"),
                                  default = ['month', 'agendaWeek', 'agendaDay'] )

    weekends = schema.Bool( title=_(u"label_weekends"),
                                  description = _(u"help_weekends"),
                                  default=True)

    firstDay = schema.Choice( title = _(u"label_firstDay"),
                                  required = True,
                                  description = _(u"help_firstDay"),
                                  source = "solgemafullcalendar.daysOfWeek",
                                  default = 1 )

    firstHour = schema.TextLine( title = _(u"label_firstHour"),
                                  required = True,
                                  description = _(u"help_firstHour"),
                                  default = u'6' )

    minTime = schema.TextLine( title = _(u"label_minTime"),
                                  required = True,
                                  description = _(u"help_minTime"),
                                  default = u'0' )

    maxTime = schema.TextLine( title=_(u"label_maxTime"),
                                  description = _(u"help_minTime"),
                                  default = u'24')

    target_folder = schema.Choice(title=_(u"label_target_folder"),
                                  description=_(u"help_target_folder"),
                                  required=False,
                                  source=CustomSearchableTextSourceBinder({'object_provides' : IATFolder.__identifier__},default_query='path:'))

    calendarHeight = schema.TextLine( title = _(u"label_calendarHeight"),
                                  required = False,
                                  description = _(u"help_calendarHeight"),
                                  default = u'600' )

    availableCriterias = schema.List( title = _(u"label_availableCriterias"),
                                  required = False,
                                  description = _(u"help_availableCriterias"),
                                  value_type = schema.Choice( title = _(u"label_availableCriterias"), source = "solgemafullcalendar.availableCriterias"),
                                  default = [] )

    displayUndefined = schema.Bool( title=_(u"label_displayUndefined"),
                                  required = False,
                                  description = _(u"help_displayUndefined"),
                                  default=False)

    def isSolgemaFullcalendar(self):
        """get name of days"""

class ISolgemaFullcalendarEvents(Interface):
    """Solgema Fullcalendar update view interface"""

class ISolgemaFullcalendarMarker(Interface):
    """A marker for items that can be displayed as solgemafullcalendar_view"""

class ISFBaseEventFields(Interface):
    """An interface that defines the specific Fullcalendar's events fields """

    allDay = schema.Bool( title=_(u"label_allDay"),
                                  description = _(u"help_allDay"),
                                  default=False)

class ISolgemaFullcalendarQuery(IViewletManager):
    """topic query for calendar"""
