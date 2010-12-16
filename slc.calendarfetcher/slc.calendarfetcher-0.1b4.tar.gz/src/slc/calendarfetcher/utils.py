from urllib2 import HTTPError
import zope.component
from Products.Archetypes.utils import addStatusMessage

def fetch_calendars(context, request, urls):
    messages = []
    title = context.Title()
    for url in urls:
        view = zope.component.queryMultiAdapter((context, request), 
                                        name='import.html', 
                                        default=None
                                    )
        try:
            message = view.import_from_url(url)
        except HTTPError, e:
            msg = "Received a '404 Not Found' error for %s" % url
            addStatusMessage(request, msg, type='error')
        else:
            msg = '%s from %s' % (message, url)
            addStatusMessage(request, msg, type='info')

        messages.append(msg)
    
    # XXX: The calendar importer in Products.Calendaring.tool changes the name
    # of the ICalendarEnhanced folder to the name of the imported folder.
    # We restore it here.
    if context.Title() != title:
        context.setTitle(title)

    return messages

