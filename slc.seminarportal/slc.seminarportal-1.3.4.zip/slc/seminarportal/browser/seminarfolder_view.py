from zope.interface import implements

from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from interfaces import ISeminarFolderView

class SeminarFolderView(BrowserView):
    """ View methods for the seminar folder view
    """
    implements(ISeminarFolderView)

    def get_seminars(self):
        """ Return brains for SPSeminar objects in context 
        """
        request = self.context.request
        if request.get('st') == 'adv' and not request.has_key('SearchableText'):
            return []

        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'portal_type':'SPSeminar', 
            'path':'/'.join(self.context.getPhysicalPath())
            }

        if request.get('st') == 'spl':
            # simple search
            searchable_text = request.get('SearchableText', '')
            query['SearchableText'] = searchable_text
            if not searchable_text:
                query['sort_on'] = 'start'
                query['sort_order'] = 'reverse'
            brains = catalog(query)

        if request.get('st') == 'adv':
            # advanced search
            date = request.get('date')
            if date:
                query['end'] = {'query':date, 'range':'min'}
                query['start'] = {'query':date.replace('00:00', '23:59'), 'range':'max'}

            location = request.get('location')
            if location:
                query['location'] = location

        brains = catalog(query)
        return list(brains)

    def date(self):
        """Return the DateTime obj
        """
        return DateTime()

    def get_countries_dict(self):
        """Return the values from the index
        """
        cutils = getToolByName(self.context, 'portal_countryutils')
        return cutils.getCountryIsoDict()

    def increment_date(self, date):
        return DateTime(date)+1

    def template_id(self):
        return '@@seminarfolder-view'

    def simple_search_headline(self):
        return 'Filter Seminar Results'

    def advanced_search_headline(self):
        return 'Advanced Seminar Filtering Options'


