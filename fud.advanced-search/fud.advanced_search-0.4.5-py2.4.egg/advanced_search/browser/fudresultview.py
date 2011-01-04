from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.AdvancedQuery import And , Eq, In, Or

from fud.advanced_search import advanced_searchMessageFactory as _


class IFudresultView(Interface):
    """
    Fudresult view interface
    """

    def getSearchItems():
        """ test method"""
        
    def __createTextQuery():
        """
        returns the query for the text search
        """
    def __listEqTuple():
        """
        Compare a list's content with a tuple's content
        """
    def __listHasElemFromTuple():
        """Compare a list's content with a tuple's content"""


class FudresultView(BrowserView):
    """
    Fudresult browser view
    """

    implements(IFudresultView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def getSearchItems(self):
        """ test method"""
        context = self.context
        request = self.request
        allowed_types = ['Quellentext','Fachartikel']
#        import pdb; pdb.set_trace()
#        Get the physical path to an object
#        The getPhysicalPath() method returns a list contained the ids of the object's containment heirarchy :
        context_path = '/'.join(context.getPhysicalPath())
        compositeQuery = And() #a query built out of many queries
        zcatQuery={}#initialize the ZCatalog styled query

        if request.DocType:
            compositeQuery.addSubquery(Eq('portal_type',request.DocType))
        else:
            doctypeQuery=Or()
            for at in allowed_types:
                doctypeQuery.addSubquery(Eq('portal_type',at))
            compositeQuery.addSubquery(doctypeQuery)

        textQuery=self.__createTextQuery()

        if textQuery:
            zcatQuery['SearchableText']=textQuery
            subQuery = self.portal_catalog.makeAdvancedQuery(zcatQuery)
            compositeQuery.addSubquery(subQuery)

        if request.subjects:
            if isinstance(request.subjects, str):
                subjects = [request.subjects]
            else:
                subjects = request.subjects

            for subj in subjects:
                compositeQuery.addSubquery(Eq('Subject',subj))

                

        if request.creators:
            if request.coop:
                creatorsQuery=And()
            else:
                creatorsQuery=Or()
            #creators were chosen in the creator field
            if isinstance(request.creators, str):
                creators=[request.creators]
            else:
                creators=request.creators
            for rc in creators:
                creatorsQuery.addSubquery(Eq('listCreators',rc))
            compositeQuery.addSubquery(creatorsQuery)
            
        if(request.notcreators):
            if isinstance(request.notcreators, str):
                creators=[request.notcreators]
            else:
                creators=request.notcreators
            for rc in creators:
                compositeQuery.addSubquery(~ Eq('listCreators',rc))


        if request.SortBy:
            #make a list out of the user input for SortBy
            sortCriteria = request.SortBy.split() 
            #validate 1st input
            if sortCriteria[0] in ('Creator','created'):
                if len(sortCriteria)>1:
                    #validate 2nd input
                    if sortCriteria[1]=='desc':
                        brains = self.portal_catalog.evalAdvancedQuery(compositeQuery,((sortCriteria[0],sortCriteria[1]),))
                else:
                    #input for direction was omitted. Default to ascending.
                    brains = self.portal_catalog.evalAdvancedQuery(compositeQuery,((sortCriteria[0]),))
        else:
            #Ignore sorting
            brains = self.portal_catalog.evalAdvancedQuery(compositeQuery)

#        query = self.createQuery()
#        query = ('listCreators':'yuda')
#        query = ['listCreators':'']
#        query['show_inactive'] = False

#            {'portal_type': 'RegionalNews',
#             'review_state': 'published',
#             'region': context.getRegion(),
#             'sort_on': 'effective',
#             'sort_order': 'descending',
#             'show_inactive': False}
#        brains = self.portal_catalog.searchResults(**query)
#        brains = self.portal_catalog.searchResults({'Creator':'yuda'})

        
#        for brain in brainsToDelete:
#            if brain in brains:
#                brains.remove(brain)
#        filteredBrains = [elem for elem in brains if elem not in brainsToDelete]
#       check if a negation query exists
#        notcreators = request.notcreators
#        if(notcreators):
#            #we have creator/s to filter out
#            #reset query
#            query=[]
#            query['listCreators']=notcreators
#            brains = brains-self.portal_catalog.searchResults(**query)
        items = []
        #rough filtering.
        #Every item, which has in its creators list a name from the requested creators
        #will be returned
        for brain in brains:
            if brain.getPath() <> context_path:
                items.append({'title':brain.Title,
                              'url':brain.getURL(),
                              'created':brain.created,
                              'Creators':brain.listCreators})

#       first get the items according to the positive query
        
        


#            for brain in brains:
#                if brain.getPath() <> context_path:
#                itemsToFilter.append({'title':brain.Title,
#                              'url':brain.getURL(),
#                              #'Creator':brain.Creator})
#                              'Creators':brain.listCreators})
#            items = positivitems-negativeitems
        return items

    def __listEqTuple(self,l,t):
        """Compare a list's content with a tuple's content"""
        if(len(l)==len(t)):
            for elem in l:
                if elem not in t:
                    return False
            return True
        else:
            return False

    def __listHasElemFromTuple(self,l,t):
        """Compare a list's content with a tuple's content"""
        for elem in l:
            if elem in t:
                return True
        else:
            return False

    def __createTextQuery(self):
        """
        returns the query for the search
        """
        request = self.request
        #dummy = request.SearchableText
        
        searchabletext=''

        if(request.AndWords):
            #AndWords is not empty
            #=> list the words and create a string with '+and+' between them
            andwords = ' and '.join(request.AndWords.split())
        else:
            andwords =  ''
        searchabletext+=andwords

        if(request.OrWords):
            if(searchabletext):
                #append to andwords
                orwords  = ' or '+' or '.join(request.OrWords.split())
            else:
                orwords  = ' or '.join(request.OrWords.split())
        else:
            orwords  = ''
        searchabletext+=orwords

        if(request.Phrase):
            if(searchabletext):
                phrase  = " and \""+' '.join(request.Phrase.split())+"\""
            else:
                phrase  = "\""+' '.join(request.Phrase.split())+"\""
        else:
            phrase  = ''
        searchabletext+=phrase
        
        if(request.NotWords):
            if(searchabletext):
                notwords  = ' and not '+' and not '.join(request.NotWords.split())
            else:
                notwords = ''
        else:
            notwords  = ''
        searchabletext+=notwords

        return searchabletext

    
