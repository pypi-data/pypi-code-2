from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner,aq_parent
from plone.memoize import instance,view
from pprint import PrettyPrinter
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from collective.multisitepanel.browser.multisitebase import MultisiteBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentsPanelView(BrowserView,MultisiteBase):

    title=_(u"Contents")
    __call__ = ViewPageTemplateFile('templates/skeleton.pt')
    details = ViewPageTemplateFile('templates/msp_contents_details.pt')
    table = ViewPageTemplateFile('templates/msp_contents_table.pt')
    
    type_order = ('Document',
                  'Event',
                  'File',
                  'Folder',
                  'Image',
                  'Large Plone Folder',
                  'Link',
                  'News Item',
                  'Topic',)

    def __init__(self, context, request):
        MultisiteBase.__init__(self, context, request)

    @instance.memoize
    def multisite_countContentsByTypes(self,this_site,content_type='all'):
        """Return an integer of the sum of content of a certain contents type in a given plone site"""
        portal_catalog = getToolByName(this_site, 'portal_catalog')
        portal_types = getToolByName(this_site, 'portal_types')
        if content_type != 'all' and content_type != 'standard':
            typeInfo = portal_types.getTypeInfo(content_type) or None
        if content_type == 'standard':
            query = {'portal_type' : self.type_order}
        elif content_type == 'all':
            query = {}
        else : query = {'portal_type' : content_type}
        contents = portal_catalog(query) or []
        if len(contents) == 0 and not typeInfo: return -1
        else : return len(contents)

    @instance.memoize
    def multisite_countCustomContents(self,this_site):
        """Return an integer of the total number of custom contents type """
        standardContents = len(self.multisite_listDefaultContentsCount(this_site).values())
        allContents = self.multisite_countContentsByType(this_site)
        return allContents - standardContents

    @instance.memoize
    def multisite_getContentTypeIcon(self,this_site,content_type):
        """Return a string with the complete url of the contents type's icon"""
        portal_types = getToolByName(this_site, 'portal_types')
        typeInfo = portal_types.getTypeInfo(content_type)
        if not typeInfo : return 'tool.gif'
        return this_site.absolute_url()+'/'+typeInfo.content_icon

    @instance.memoize
    def listStandardTypes(self):
        """Return a list of standard contents type's info"""
        ret = []
        portal_types = getToolByName(self.context, 'portal_types')
        for content_type in self.type_order :
            typeInfo = portal_types.getTypeInfo(content_type) or ()
            ret.append(typeInfo)
        return ret

    @instance.memoize
    def multisite_getCustomContentList(self):
        """Return a list of tuples. Each tuple is structured of typeInfo, and a list of sites where is present"""
        ret = {}
        cmf_types = ('ChangeSet','TempFolder','Discussion Item','Plone Site','Favorite')
        for site in self.sitesList:
            portal_types = getToolByName(site[1], 'portal_types')
            siteTypeList = portal_types.listTypeTitles()
            for content_type in siteTypeList:
                if content_type.find('Criteri') == -1 and content_type not in cmf_types and content_type not in self.type_order:
                    typeInfo = portal_types.getTypeInfo(content_type) or ()
                    if content_type in ret.keys(): ret[content_type]['sitesList'].append(site[1])
                    else:
                        ret[content_type] = {}
                        ret[content_type]['typeInfo'] = typeInfo
                        ret[content_type]['sitesList'] = [site[1],]
        items = ret.items()
        items.sort(lambda x,y: cmp(x[1]['typeInfo'].product,y[1]['typeInfo'].product))
        return [(x[1]['typeInfo'],x[1]['sitesList']) for x in items]

    @instance.memoize
    def multisite_customContentsBySite(self,this_site):
        """Return a list of custom contents types in a given site"""
        ret = []
        cmf_types = ('ChangeSet','TempFolder','Discussion Item','Plone Site','Favorite')
        portal_types = getToolByName(this_site, 'portal_types')
        siteTypeList = portal_types.listTypeTitles()
        for content_type in sorted(siteTypeList):
            if content_type.find('Criteri') == -1 and content_type not in cmf_types and content_type not in self.type_order:
                typeInfo = portal_types.getTypeInfo(content_type) or ()
                ret.append((typeInfo,self.multisite_countContentsByTypes(this_site,typeInfo.getId())))
        return sorted(ret,key= lambda content: content[0].product)
