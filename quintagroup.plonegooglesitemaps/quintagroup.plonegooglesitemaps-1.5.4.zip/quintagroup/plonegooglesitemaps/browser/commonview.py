from string import find
from zope.interface import implements, Interface, Attribute

from Acquisition import aq_inner, aq_parent
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from quintagroup.plonegooglesitemaps import qPloneGoogleSitemapsMessageFactory as _
from quintagroup.plonegooglesitemaps.browser.utils import additionalURLs, applyOperations


class ISitemapView(Interface):
    """
    Sitemap view interface
    """

    def results():
        """ Return list of dictionary objects
            which confirm Sitemap conditions
        """

    def getAdditionalURLs():
        """ Return additional URL list
        """

    def updateRequest():
        """ Add compression header to RESPONSE
            if allowed
        """

    numEntries = Attribute("Return number of entries")

class CommonSitemapView(BrowserView):
    """
    Sitemap browser view
    """
    implements(ISitemapView)

    # key, function map for extend return results
    # with mapping data
    additional_maps = ()


    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def search_path(self):
        return '/'.join(aq_parent(aq_inner(self.context)).getPhysicalPath())

    def getFilteredObjects(self):
        """ Return brains
        """
        return []

    def results(self):
        """ Prepare mapping for template
        """
        result = []
        objects = self.getFilteredObjects()
        blackout_list = self.context.getBlackout_list()
        reg_exps = self.context.getReg_exp()

        brain_url_map = applyOperations([ob for ob in objects 
            if (ob.getId not in blackout_list)],
            reg_exps)

        # Prepare dictionary for view
        for url, b in brain_url_map.items():
            res_map = {'url' : url,}
            [res_map.update({k : f(b)}) for k, f in self.additional_maps]
            result.append(res_map)
        self.num_entries = len(result)
        return result

    def updateRequest(self):
        self.request.RESPONSE.setHeader('Content-Type', 'text/xml')
        try:
            compression = self.context.enableHTTPCompression()
            if compression:
                compression(request=self.request)
        except:
            pass

    def getAdditionalURLs(self):
        return additionalURLs(self.context)

    @property
    def numEntries(self):
        return len(self.results()) + len(self.getAdditionalURLs())
