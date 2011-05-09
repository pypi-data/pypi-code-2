from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class Data(BrowserView):
    """View class providing the data for the summary statistics"""

    def catalog(self):
        return getToolByName(self, 'portal_catalog')

    def getTypes(self):
        """Return a list of dictionaries of format
        {'portal_type': <some type>, 'number' : <number of items>}
        """
        ct = self.catalog()
        existing_types = ct.uniqueValuesFor('portal_type') 
        result = []
        for t in existing_types:
            result.append(dict(portal_type = t,
                               number = len(ct(portal_type=t))
                               ))
        return result

    def getStates(self):
        """Return a list of dictionaries of format
        {'state': <some state>, 'number' : <number of items in state>}
        """
        ct = self.catalog()
        existing_states = ct.uniqueValuesFor('review_state') 
        result = []
        for s in existing_states:
            result.append(dict(state = s,
                               number = len(ct(review_state=s))
                               ))
        return result

    def getCount(self, portal_type, review_state):
        """Return the number of content items of type <portal_type> in state
        <review_state>"""
        ct = self.catalog()
        return len(ct(portal_type=portal_type, review_state=review_state))

    def now(self):
        """The current date and time"""
        return DateTime().ISO()

    def total(self):
        """The total number of content items"""
        return len(self.catalog()())


class Export(Data):
    """
    Provide the statistics data in CSV format for download
    """
    
    def csv(self, line_sep="\n\r", separator=", "):
        """Export the data matrix to CSV (Comma Separated Values) format"""

        lines = []

        line = ['Portal Type|Review State']
        for s in self.getStates():
            line.append(s['state'])
        line.append('total')
        lines.append(separator.join(line))
            
        for t in self.getTypes():
            line = ["%s"%t['portal_type']]
            for s in self.getStates():
                c = self.getCount(t['portal_type'],s['state'])
                line.append('%s'%c)
            line.append("%s"%t['number'])
            lines.append(separator.join(line))

        line = ['total']
        for s in self.getStates():
            line.append("%s"%s['number'])
        line.append("%s"%self.total())
        lines.append(separator.join(line))

        response = line_sep.join(lines)

        self.request.response.setHeader('Content-Type', 'application/x-msexcel')
        self.request.response.setHeader("Content-Disposition", 
                                        "inline;filename=contentstatistics.csv")
        
        return response
