from zope.interface import implements
from zope.component import adapts

from Products.Archetypes.utils import shasattr
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName

from ZTUtils.Zope import make_query

from betahaus.contextcloud.interfaces import IContextCloud


class Tag(object):
    """ It's a lot simpler to keep track of objects than dicts with lots of keys.
    """
    def __init__(self, name=u'', weight=0, count=0, url=None, selected=False):
        self.name = name
        self.weight = weight
        self.count = count
        self.url = url
        self.selected = False


class ContextCloud(object):
    """ Create a cloud based on the current context.
    """
    implements(IContextCloud)
    adapts(IFolderish)
    
    def __init__(self, context):
        self.context = context
        self._catalog = getToolByName(self.context, 'portal_catalog')

    def _query_catalog(self):
        """ Returns the brains in this context based on the type of context.
            If it's a Topic/Collection/Smartfolder/Whatevernewnametheycomeupwith
            the queryCatalog method will be used, otherwise getFolderContents
            will be used.
            Both methods should blank out any sorting options, since this is used
            to generate tag listings and not actual results.
        """
        #Topic?
        if shasattr(self.context, 'queryCatalog'):
            #This is something collection-like and needs to be handled in a special way
            #since it could have a limit set on itself, which it will honor.
            query =  self.context.buildQuery()
            return self._catalog(query)
        
        #If not it's probably a normal folder
        return self.context.getFolderContents()      

    def getResults(self, index='Subject', nosort=False):
        """ Count occurences of keys in all indexes used. """
        #Make sure the index we want to use exist as a column in
        #portal catalog. Otherwise we won't be able to calculate the tags.
        if index not in self._catalog.schema():
            raise KeyError("%s doesn't exist as a column in the portal_catalog" % index)
        counter = {}
        for brain in self._query_catalog():
            #It could be a list or a string
            values = getattr(brain, index)
            if type(values) == str:
                values = [values]
            for v in values:
                if v not in counter:
                    counter[v] = Tag(name=v, count=1)
                else:
                    counter[v].count += 1
        
        tags = self._url_info(counter.values(), index=index)
        
        if nosort:
            return tags
        return sorted(tags, key=lambda x: x.name)

    def addCloud(self, tags, levels=5):
        """ This methods append cloud information for the tags already used. """
        counts = set([x.count for x in tags])
        maxkey = max(counts)
        minkey = min(counts)
        
        thresholds = [pow(maxkey - minkey + 1, float(i) / float(levels)) for i in range(0, levels)]
        
        for tag in tags:
            weight = 0
            for t in thresholds:
                weight += 1
                if tag.count <= t:
                    break
            tag.weight = weight
        return tags

    def _url_info(self, tags, base_url=None, index='Subject'):
        """ Add URL and selected information to tags.
        """
        request = self.context.REQUEST
        if base_url is None:
            base_url = self.context.absolute_url()

        #Modifying the content filter should change the types displayed
        if not hasattr(request, 'contentFilter'):
            request.contentFilter = {}
            
        contentFilter = request.contentFilter
        
        for tag in tags:
            #It's important to copy the request since we don't want to modify the original one.
            query = request.form.copy()
            #Selected?
            if index in query and tag.name == query[index]:
                #Tag is selected
                tag.selected = True
                contentFilter[index] = tag.name
                #Clicking it should deselect it
                del query[index]
            else:
                #Tag is not selected
                query[index] = tag.name

            #Keep anything else in the request intact
            if query:
                tag.url = "%s?%s" % (base_url, make_query(query))
            else:
                tag.url = base_url
        return tags
