from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Search(BrowserView):
    """ Simple and advanced search functionality for slc.seminar
    """

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
        return '@@seminar-search'

    def simple_search_headline(self):
        return 'Search for Seminars, Speakers or Speeches'

    def search(self):
        """ Return brains for all the seminar related objects
        """
        request = self.context.request
        if not request.has_key('SearchableText'):
            return []
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'portal_type':['SPSeminar', 'SPSpeech', 'SPSpeaker', 'SPSpeechVenue']
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


