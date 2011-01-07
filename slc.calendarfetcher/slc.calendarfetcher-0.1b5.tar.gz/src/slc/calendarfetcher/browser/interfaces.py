from zope import schema
from zope import interface
from plone.theme.interfaces import IDefaultPloneLayer
from z3c.form import button
from slc.calendarfetcher import calendarfetcher_messagefactory as _

class ICalendarFetcherLayer(IDefaultPloneLayer):
    """ Marker Interface used by BrowserLayer
    """

class IConfigForm(interface.Interface):
    """ Base Schema for the edit form. It is dynamically extended by plugins
    """
    calendar_urls = schema.Text(
                        title=_(u"Calendar URLs"),
                        description=_(
                            u" Please provide a list of ICS calendar URL "
                            u"addresses, each one on a new line. This "
                            u"calendar can then be updated "
                            u"with events from these remote calendars."
                            ),
                        required=True,
                        ) 
    add_url = button.Button(title=_(u"Save"))
    add_and_refresh = button.Button(title=_(u"Save and fetch the calendars"))


class IFetcherConfigView(interface.Interface):
    """ Marker interface
    """

class ICalendarFetcherUtils(interface.Interface):
    """ Marker interface
    """

    def is_calendar_enhanced(self):
        """ """

    def fetch_remote_calendars(self):
        """ """

    def fetch_all_remote_calendars(self):
        """ """

