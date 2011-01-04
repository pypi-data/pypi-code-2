from urllib import splithost
from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.AdvancedQuery import And , Eq, Or



class IAdvancedsearchView(Interface):
    """
    Fudresult view interface
    """

    def getSearchItems():
        """ test method"""

    def getPathToSearch():
        """
        return path to the source folder by using HTTP_REFERER
        """

    def getCreators():
        """
        returns all creators who have a full name specified
        """
    def isSorterTitle():
        """retturns true if the sorter is a title"""
    def isSorterTitleDesc():
        """retturns true if the sorter is a Title descending"""
    def isSorterCreator():
        """retturns true if the sorter is a Creator"""
    def isSorterCreatorDesc():
        """retturns true if the sorter is a Creator descending"""
    def isSorterDate():
        """retturns true if the sorter is a Date"""
    def isSorterDateDesc():
        """retturns true if the sorter is a Date descending"""
    def __createTextQuery():
        """
        returns the query for the text search
        """
    def __getSearchTerm():
        """
        returns the first search term found in the text fields.
        The returned value is used to append it as a searchterm parameter
        when the hyperlink of one of the search results is clicked.
        """
    def __listEqTuple():
        """
        Compare a list's content with a tuple's content
        """
    def __listHasElemFromTuple():
        """Compare a list's content with a tuple's content"""


class AdvancedsearchView(BrowserView):
    """
    Fudresult browser view
    """

    implements(IAdvancedsearchView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
#        self.searchPath = ''
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')

    def isSorterTitle(self):
        """retturns true if the sorter is a title"""
        return self.request.SortBy=='sortable_title'

    def isSorterTitleDesc(self):
        """retturns true if the sorter is a Title descending"""
        return self.request.SortBy=='sortable_title desc'

    def isSorterCreator(self):
        """retturns true if the sorter is a Creator"""
        return self.request.SortBy=='Savedby'

    def isSorterCreatorDesc(self):
        """retturns true if the sorter is a Creator descending"""
        return self.request.SortBy=='Savedby desc'

    def isSorterDate(self):
        """retturns true if the sorter is a Date"""
        return self.request.SortBy=='modified'

    def isSorterDateDesc(self):
        """retturns true if the sorter is a Date descending"""
        return self.request.SortBy=='modified desc'

    def getCreators(self):
        """
        returns the query for the text search
        """
        creators = []
        candidates = self.portal_catalog.uniqueValuesFor('listCreators')
        for can in candidates:
            #check whether it has a last name
            if self.portal_membership.getMemberInfo(can):
                creators.append(can)
        return creators

    def __getSearchTerm(self):
        """
        returns the first search term found in the text fields.
        The returned value is used to append it as a searchterm parameter
        when the hyperlink of one of the search results is clicked.
        """
        request = self.request
        
        st="?searchterm="
        if request.AndWords:
            return st+request.AndWords
        if request.OrWords:
            return st+request.OrWords
        if request.Phrase:
            return st+request.Phrase

    
    def getPathToSearch(self):
        """
        return path to the source folder by using HTTP_REFERER or request.path
        """
        request = self.request
        if request.has_key('searchpath'):
            if request.searchpath:
                return request.searchpath
        
        if request['HTTP_REFERER']==request['URL'] or \
           request['SERVER_URL']+self.portal_url.getPortalPath()==request['HTTP_REFERER']:
            #calling_path is the same as current_path. we are in the root
            return  False

#path example
#http://localhost:8080/plone-site/advanced_search?b_start=0&AndWords=&OrWords=&Phrase=&NotWords=&coop=&creators=&notcreators=&DocType=Quellentext&SortBy=modified+desc&bsize=5&submit=Suchen
        #Remove schema ('http:') to get something like
        #'//localhost:8080/one/two/three' from the HTTP_REFERER
        referer = request['HTTP_REFERER'][5:]

        #drop the host and port from the address and eventually parameters
        # returns something like '/one/two/three'
        ref_path = (splithost(referer)[1].split('?'))[0]

        #check if we're not coming from advanced_search
        path_as_list = ref_path.split('/')
        tmp = path_as_list[len(path_as_list)-1]
        if tmp=='advanced_search':
            return False

        #get the object by its (string) path
        obj = self.portal.restrictedTraverse(ref_path)

        #check if obj is not a bound method
        if not hasattr(obj, 'getPhysicalPath'):
            #drop the method from the path and get the object again
            tmp = ref_path.split('/')
            ref_path='/'.join(tmp[:len(tmp)-1])
            obj = self.portal.restrictedTraverse(ref_path)

        phys_path=obj.getPhysicalPath()

        if not obj.isPrincipiaFolderish:
            #item was detected. we want a folder. remove the item part from the path
            #folder_path = ('->'.join(phys_path[:len(phys_path)-1]))[2:]
            #self.searchPath = '/'.join(phys_path[:len(phys_path)-1])
            folder_path= '/'.join(phys_path[:len(phys_path)-1])
            #check if we are coming from the root folder of the site
            if folder_path==self.portal_url.getPortalPath():
                return False;
        else:
            #folder_path = ('->'.join(phys_path))[2:]
            #self.searchPath = '/'.join(phys_path)
            folder_path = '/'.join(phys_path)

        return folder_path
    
    def getSearchItems(self):
        """ test method"""
        context = self.context
        request = self.request
        allowed_types = ['Quellentext','Fachartikel']
        #batch start specification
        searchTerm=""
        
        
#        import pdb; pdb.set_trace()
#        Get the physical path to an object
#        The getPhysicalPath() method returns a list contained the ids of the object's containment heirarchy :

        #context_path = '/'.join(context.getPhysicalPath())
        compositeQuery = And() #a query built out of many queries
        zcatQuery={}#initialize the ZCatalog styled query


        if  request.has_key('pathsearch'):

#            import pdb; pdb.set_trace()
            if request.pathsearch:
                #The user has marked the path
                compositeQuery.addSubquery(Eq('path',request.searchpath))

        if request.DocType:
            compositeQuery.addSubquery(Eq('portal_type',request.DocType))
        else:
            doctypeQuery=Or()
            for at in allowed_types:
                doctypeQuery.addSubquery(Eq('portal_type',at))
            compositeQuery.addSubquery(doctypeQuery)

        textQuery=self.__createTextQuery()

        if textQuery:
            #search term for the highlighting of text
            searchTerm+=self.__getSearchTerm()
            zcatQuery['SearchableText']=textQuery
            subQuery = self.portal_catalog.makeAdvancedQuery(zcatQuery)
            compositeQuery.addSubquery(subQuery)

        if request.has_key('subjects'):
            if  request.subjects:
                if isinstance(request.subjects, str):
                    subjects = [request.subjects]
                else:
                    subjects = request.subjects

                subjectsQuery=Or()
                for subj in subjects:
                    subjectsQuery.addSubquery(Eq('Subject',subj))
                compositeQuery.addSubquery(subjectsQuery)
                

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
            
#        if(request.notcreators):
#            if isinstance(request.notcreators, str):
#                creators=[request.notcreators]
#            else:
#                creators=request.notcreators
#            for rc in creators:
#                compositeQuery.addSubquery(~ Eq('listCreators',rc))


        
        listSortKey=''
        listSortDesc=False
        if request.SortBy:
            #make a list out of the user input for SortBy
            sortCriteria = request.SortBy.split() 
            #validate 1st input
#            if sortCriteria[0]=='Creator'
            if sortCriteria[0] in ('Savedby'):
                listSortKey=sortCriteria[0];
                brains = self.portal_catalog.evalAdvancedQuery(compositeQuery)
                if len(sortCriteria)>1:
                    #validate 2nd input
                    if sortCriteria[1]=='desc':
                         listSortDesc=True
            elif sortCriteria[0] in ('modified','sortable_title'):
                if len(sortCriteria)>1:
                    if sortCriteria[1]=='desc':
                        brains = self.portal_catalog.evalAdvancedQuery(compositeQuery,((sortCriteria[0],sortCriteria[1]),))
                else:
                    brains = self.portal_catalog.evalAdvancedQuery(compositeQuery,((sortCriteria[0]),))
        else:
            #Ignore sorting
            brains = self.portal_catalog.evalAdvancedQuery(compositeQuery)

        items = []
        #rough filtering.
        #Every item, which has in its creators list a name from the requested creators
        #will be returned
        for brain in brains:
            #if brain.getPath() <> context_path:
            savedby = self.portal_membership.getMemberInfo(brain.Creator)['fullname']
            creators=[]
            for creator in brain.listCreators:
                creators.append(self.portal_membership.getMemberInfo(creator)['fullname'])
            #for each item(document) create a dictionary of key:value pairs.
            items.append({'Title':brain.Title,
                          'Type':brain.Type,
                          'url':brain.getURL()+searchTerm,
                          'created':brain.created,
                          'modified':brain.modified,
                          'Creators':creators,
                          'Savedby':savedby,
                          'subjects':brain.Subject,
                          'fundort':brain.fundort,
                          'druckort':brain.druckort,
                          'uid':brain.UID})


        if listSortKey:
            #Sorting was requested => sort the list of items before returning them.
            items.sort(key=lambda i: i[listSortKey],reverse=listSortDesc)

        return items

    def __createTextQuery(self):
        """
        returns the queryString for the search
        """
        request = self.request
        
        searchabletext=''
        if(request.AndWords):
            #AndWords is not empty
            #=> list the words and create a string with ' and ' between them
            andwords = '('+' and '.join(request.AndWords.split())+')'
        else:
            andwords =  ''
        searchabletext+=andwords

        if(request.OrWords):
            if(searchabletext):
                #append to andwords
                #split OrWords to a list and join them with an 'or' between each word
                orwords  = ' or ('+' or '.join(request.OrWords.split())+')'
            else:
                #The same but without the appending to andwords
                orwords  = '('+' or '.join(request.OrWords.split())+')'
        else:
            orwords  = ''
        searchabletext+=orwords

        if(request.Phrase):
            if(searchabletext):
                phrase  = " or \""+' '.join(request.Phrase.split())+"\""
            else:
                phrase  = "\""+' '.join(request.Phrase.split())+"\""
        else:
            phrase  = ''
        searchabletext+=phrase
        
        if(request.NotWords):
            #for each word in the notwords-field append the string " and not "
            #this works only if searchabletext is not empty
            if(searchabletext):
                notwords  = ' and not '+' and not '.join(request.NotWords.split())
            else:
                notwords = ''
        else:
            notwords  = ''
        searchabletext+=notwords

        return searchabletext

    
