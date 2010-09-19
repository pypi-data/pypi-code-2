from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from Products.ATContentTypes.interface.interfaces import ICalendarSupport
from Products.ATContentTypes.interface.topic import IATTopic
from Products.ATContentTypes.interface.folder import IATFolder

from simplejson.encoder import JSONEncoder

class IEventsView(Interface):
    """ get events view interface """
        
    def getEvents(start=None, end=None):
        """ returns all object implementing ICalendarSupport and matching the
        criterias """

    def getJSONEvents(start=None, end=None):
        """ returns all object implementing ICalendarSupport and matching the
        criterias jsonfied """
        
    def _encodeJSON(data):
        """ encodes given data in json """
        
    def _buildDict(brain):
        """ builds a dict from a given brain """
        
class EventsView(BrowserView):
    """  """
    implements (IEventsView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, *args, **kw):
        start = self.request.get('start', None)
        end = self.request.get('end', None)

        return self.getJSONEvents(start, end)      
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    def getJSONEvents(self, start=None, end=None):
        """ returns all object implementing ICalendarSupport and matching the criterias """        
        return self._encodeJSON(self.getEvents(start, end))
    
    def _encodeJSON(self, data):
        """ takes whats given and jsonfies it """
        return JSONEncoder().encode(data)
        
    def getEvents(self, start=None, end=None):
        """ searches the catalog for event like objects in the given time frame """
        query_func = self.portal_catalog.searchResults
        if IATFolder.providedBy(self.context):
            query_func = self.context.getFolderContents
        elif IATTopic.providedBy(self.context) and self.context.buildQuery() is not None:
            ## check buildQuery result, otherwise the collection will return nothing
            query_func = self.context.queryCatalog
        
        query = {'object_provides': ICalendarSupport.__identifier__}
        if start:
            query['start'] = {'query': DateTime(int(start)), 'range':'min'}
        if end:
            query['end'] = {'query': DateTime(int(end)), 'range': 'max'} 
        
        brains = query_func(query)
                
        jret = []
        for brain in brains:
            jdict = self._buildDict(brain)
            jret.append(jdict)
        return jret        

    def _buildDict(self, brain=None):
        """ builds a dict from the given brain, suitable for the fullcalendar javascript """
        jdict = {}
        if brain:
            allDay = False            
            if brain.start== brain.end:
                allDay = True
            jdict = {'title' : brain.Title, 'start' : str(brain.start), 'end' : str(brain.end), 'allDay' : allDay, 'url' : brain.getURL()}
        return jdict
