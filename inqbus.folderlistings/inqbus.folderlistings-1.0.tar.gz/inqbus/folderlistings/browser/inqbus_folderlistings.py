from zope.interface import implements, Interface
from zope.component import queryUtility, getMultiAdapter
from Products.Five import BrowserView
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from inqbus.folderlistings import _

try:
    from inqbus.plone.fastmemberproperties.interfaces \
                                            import IFastmemberpropertiesTool
    HAS_FMB = True
except ImportError:
    HAS_FMB = False

class IFolderlisting(Interface):
    """ """
    
class Folderlisting(BrowserView):
    """
    """
    implements(IFolderlisting)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        if hasattr(self.request, 'sort_on'):
            self.sort_on = self.request.sort_on
        else:
            self.sort_on = 'modified'
        if self.sort_on == 'modified':
            self.sort_order = 'descending'
        else:
            self.sort_order = 'ascending'
        self.folderlist = []
        self.other_resultlist = []
        self.resultlist = []
        self.sortlinks = {}
        if self.context.portal_type == 'Folder':
            self.sortlinks = {'title':self.context.absolute_url() + \
                                                     '?sort_on=sortable_title',
                              'author':self.context.absolute_url() + \
                                                     '?sort_on=Creator',
                              'type':self.context.absolute_url() + \
                                                     '?sort_on=portal_type',
                              'modified_stamp':self.context.absolute_url() + \
                                                     '?sort_on=modified',}
        
    def __call__(self):
        """
        """
        self.build_childlists()
        self.resultlist = self.folderlist + self.other_resultlist
        return self.index()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def member_tool(self):
        return self.context.portal_membership
        
    @property    
    def fm_tool(self):
        if not HAS_FMB:
            return None
        return queryUtility(IFastmemberpropertiesTool, 
                                                    'fastmemberproperties_tool')

    def build_childlists(self):
        """
        """
        show_inactive = self.member_tool.checkPermission(
                                              'Access inactive portal content', 
                                               self.context)
        if self.context.portal_type == 'Folder':
            cur_path = '/'.join(self.context.getPhysicalPath())
            path = {}
            path['query'] = cur_path
            path['depth'] = 1
            folderquery = {'path': path,
                           'portal_type':'Folder',
                           'sort_order':self.sort_order,
                           'sort_on':self.sort_on
                           }
            folderresults = self.portal_catalog(folderquery, show_all=1,
                                                    show_inactive=show_inactive)
        elif self.context.portal_type == 'Topic':
            folderresults = self.context.queryCatalog(portal_type='Folder')
        for folderbrain in folderresults:
            modification_date = self.get_modification_date(folderbrain)
            author = self.get_author_infos(folderbrain.Creator)
            folderdict = {'title':folderbrain.Title,
                         'author':author['title_or_id'],
                         'author_url':self.context.portal_url() + \
                                      "/author/"+author['id'],
                         'type':folderbrain.portal_type,
                         'last_modified':modification_date,
                         'url':folderbrain.getURL(),
                         'class':'contenttype-'+folderbrain.portal_type.lower(),
                         'file_type':None}
            self.folderlist.append(folderdict)
        if self.context.portal_type == 'Folder': 
            query = {'path': path,
                     'sort_on':self.sort_on,
                     'sort_order':self.sort_order}
            childs = self.portal_catalog.queryCatalog(query, show_all=1,
                                                    show_inactive=show_inactive)
        elif self.context.portal_type == 'Topic':
            childs = self.context.queryCatalog()
        for child in childs:
            if child.portal_type != 'Folder':
                modification_date = self.get_modification_date(child)
                author = self.get_author_infos(child.Creator)
                if child.portal_type == 'File':
                    type = 'document'
                else:
                    type = child.portal_type.lower()
                childdict = {'title':child.Title,
                         'author':author['title_or_id'],
                         'type':child.portal_type,
                         'last_modified':modification_date,
                         'url':child.getURL(),
                         'class':'contenttype-'+type,}
                if author['id']:
                    childdict['author_url'] = self.context.portal_url() + \
                                              "/author/"+author['id']
                else:
                    childdict['author_url'] = None
                self.other_resultlist.append(childdict)
                
    def get_author_infos(self, userid):
        """
        """
        authorinfos = {}
        if self.fm_tool:
            author = self.fm_tool.get_properties_for_member(userid)
            if author:
                if author['fullname']:
                    authorinfos['title_or_id'] = author['fullname']
                else:
                    authorinfos['title_or_id'] = userid
                authorinfos['id'] = userid
                return authorinfos
        author = self.member_tool.getMemberById(userid)
        if author:
            authorinfos['title_or_id'] = author.title_or_id()
            authorinfos['id'] = author.id
        else:
            authorinfos['title_or_id'] = userid
            authorinfos['id'] = None
        return authorinfos
    
    def get_modification_date(self, brain):
        """
        """
        ploneview = getMultiAdapter((self.context, self.request), name=u'plone')
        return ploneview.toLocalizedTime(brain.ModificationDate)