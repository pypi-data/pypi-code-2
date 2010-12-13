import logging
import Acquisition 

from zope import component
from zope import interface
from zope.annotation.interfaces import IAnnotations

from z3c.form import form
from z3c.form import field
from z3c.form import button
from z3c.form import validator

from plone.z3cform import z2
try:
    # Only available from version 0.6 onwards
    from plone.z3cform.interfaces import IWrappedForm
    IWrappedForm = IWrappedForm # Pyflakes
except:
    IWrappedForm = None
from plone.z3cform.layout import FormWrapper

from Products.Archetypes.utils import addStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from p4a.calendar.interfaces import ICalendarEnhanced

from slc.calendarfetcher.validators import TextLineURLValidator
from slc.calendarfetcher import calendarfetcher_messagefactory as _
from slc.calendarfetcher import utils
import interfaces

log = logging.getLogger('slc.calendarfetcher.browser.configform.py')



class ConfigForm(form.Form):
    """ """
    label = _(u"Configuration Settings for the Calendar fetcher")
    ignoreContext = True
    fields = field.Fields(interfaces.IConfigForm).select('calendar_urls',)
    buttons = button.Buttons(interfaces.IConfigForm).select(
                                                        'add_url',
                                                        'add_and_refresh'
                                                        )

    def updateWidgets(self):
        '''See interfaces.IForm'''
        form.Form.updateWidgets(self)
        self.widgets['calendar_urls'].rows = 10
        annotations = IAnnotations(self.context)
        widget_value = self.request.get('form.widgets.calendar_urls')
        if not widget_value:
            urls = annotations.get('slc.calendarfetcher-urls', [])
            widget_value = u'\n'.join(unicode(v) for v in sorted(urls or []))

        self.widgets['calendar_urls'].value = widget_value

    @button.handler(interfaces.IConfigForm['add_url'])
    def add_url(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = '\n'.join([error.error.__str__() for error in errors])
            return 

        urls = []
        if data.has_key('calendar_urls'):
            urls = [v.strip() for v in data['calendar_urls'].split()]

        annotations = IAnnotations(self.context)
        annotations['slc.calendarfetcher-urls'] = urls
        addStatusMessage(self.request, 'URLs Saved', type='info')
        self.request.response.redirect(self.context.REQUEST.get('URL'))

    @button.handler(interfaces.IConfigForm['add_and_refresh'])
    def add_and_refresh(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = _(
                    "Please correct the following errors before saving the form"
                    )
            return 

        if data.has_key('calendar_urls'):
            urls = [v for v in data['calendar_urls'].split()]
            utils.fetch_calendars(self.context, self.request, urls)
        else:
            urls = []

        annotations = IAnnotations(self.context)
        annotations['slc.calendarfetcher-urls'] = urls
        addStatusMessage(self.request, 'URLs Saved', type='info')
        self.request.response.redirect(self.context.REQUEST.get('URL'))


class FetcherConfigView(FormWrapper):
    """ """
    interface.implements(interfaces.IFetcherConfigView)
    id = u'calendar_urls.html'
    label = _(u"Configuration Settings for the Calendar fetcher")
    form = ConfigForm

    def __init__(self, context, request):
        super(FetcherConfigView, self).__init__(context, request)
        self.form_instance = self.form(self.context, self.request)
        if IWrappedForm is not None:
            interface.alsoProvides(self.form_instance, IWrappedForm)

    def update(self):
        z2.switch_on(self, request_layer=self.request_layer)
        self.form_instance.update()

    def contents(self):
        z2.switch_on(self, request_layer=self.request_layer)
        # XXX really messed up hack to support plone.z3cform < 0.5.8
        # We call the form to make the widgets property available on it,
        # otherwise view/widgets fails
        self.form_instance()
        return self.form_instance.render()

    def render_form(self):
        """This method combines the individual forms and renders them.
        """
        return self.form_instance()


# set conditions for which fields the validator class applies
validator.WidgetValidatorDiscriminators(
                        TextLineURLValidator,
                        field=interfaces.IConfigForm['calendar_urls']
                        )

# Register the validator so it will be looked up by z3c.form machinery
component.provideAdapter(TextLineURLValidator)


class CalendarFetcherUtils(BrowserView):
    """ """
    interface.implements(interfaces.ICalendarFetcherUtils)
    id = u'calendar_urls.html'
    label = _(u"Configuration Settings for the Calendar fetcher")

    def is_calendar_enhanced(self):
        """ """
        context = Acquisition.aq_inner(self.context)
        return ICalendarEnhanced.providedBy(context)

    def fetch_calendars(self):
        """ """
        messages = {}
        if not self.is_calendar_enhanced():
            return 'Not an ICalendarEnhanced object'
            
        calendar = Acquisition.aq_inner(self.context)
        annotations = IAnnotations(calendar)
        urls = annotations['slc.calendarfetcher-urls']
        messages['/'.join(calendar.getPhysicalPath())] = \
                utils.fetch_calendars(calendar, self.request, urls)

        return messages

    def fetch_all_calendars(self):
        """ """
        messages = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
                    object_provides="p4a.calendar.interfaces.ICalendarEnhanced"
                    )
        for brain in brains:
            calendar = brain.getObject()
            annotations = IAnnotations(calendar)
            urls = annotations['slc.calendarfetcher-urls']
            messages[brain.getURL()] = utils.fetch_calendars(calendar, self.request, urls)

        return messages


