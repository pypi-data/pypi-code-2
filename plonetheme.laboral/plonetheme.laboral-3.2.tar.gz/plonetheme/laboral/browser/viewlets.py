from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter
import time
import string
from zope.interface import implements
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.WorkflowCore import WorkflowException

#Hard dependencies
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IAudio

class FooterView (BrowserView):
    """
    Footer menu. Reads the /footer page and generates a footer menu.
    A link to login_form will generate the default login menu with dropdown menu
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('footer.pt')

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        
    def getFooterObject(self):
        urltool = getToolByName(self.context, 'portal_url')
        languagetool = getToolByName(self.context, 'portal_languages')
        portal = urltool.getPortalObject()
        try:
            lang = self.context.getLanguage()
        except:
            lang = languagetool.getDefaultLanguage()
            
        if lang == '':
            lang = "en"
	
	if hasattr(portal, lang):	 
	    if hasattr(portal[lang], "footer"):
	       return portal[lang].footer
	    else:
		return None
	else:
	    if hasattr(portal, "footer"):
	       return portal.footer
	    else:
		return None
        
    def generateFooter(self):
        footer = self.getFooterObject()
        if footer is not None:
            body = footer.getText()
            return body
        else:
            return ""
        
        
        
class GlobalSectionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('sections.pt')

    def update(self):
        context = aq_inner(self.context)
        portal_tabs_view = getMultiAdapter((context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs()

        self.selected_tabs = self.selectedTabs(portal_tabs=self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']

    def getSubItems(self, tab):
	'''Get items for submenu
	'''
	portal = self.context.restrictedTraverse("@@plone_portal_state").portal()
	#----The URL way to get the child items which turned out to suck big time------
	#tabPath = tab['url']
	#path = tabPath.split("/")
	#queryPath = "/" + "/".join(path[-3:])
	#catalog = getToolByName(self, 'portal_catalog')
	#results = catalog.searchResults(path = {'query' : queryPath, 'depth' : 1 }, sort_on='getObjPositionInParent')
	#------------------------------------------------------------------------------	
	if hasattr(self.context, 'getLanguage'):
	    lang = self.context.getLanguage()
	    if lang == '':
		return []
	    item = portal[lang][tab['id']]
	else:
	    item = portal[tab['id']]
	    
	results = item.objectValues()
	
	portal_workflow = getToolByName(self, 'portal_workflow')
	subitems = []
	for item in results:
	    if hasattr(item, "getObject"):
		obj = item.getObject()
	    else:
		obj = item
	    try:
		if not obj.exclude_from_nav() and portal_workflow.getInfoFor(obj, 'review_state') == 'published' or not getToolByName(self,'portal_membership').isAnonymousUser():
		    subitems.append(obj)
	    except WorkflowException:
		if not obj.exclude_from_nav():
		    subitems.append(obj)
		
	return subitems
	

    def selectedTabs(self, default_tab='index_html', portal_tabs=()):
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]

        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            if path.startswith(action_path):
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path), action['id']))

        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal' : valid_actions[-1][1]}

        return {'portal' : default_tab}
        
class SliderViewlet(BrowserView):
    implements(IViewlet)
    render = ViewPageTemplateFile('slider.pt')
    
    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
    
    def currenttime(self):
	return time.time()
    
    def trimDescription(self, desc, num):
	if len(desc) > num: 
		res = desc[0:num]
		lastspace = res.rfind(" ")
		res = res[0:lastspace] + " ..."
		return res
	else:
		return desc

    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        try:
            return util.ulocalized_time(time, long_format, time_only, self.context,
                                        domain='plonelocales')
        except TypeError: # Plone 3.1 has no time_only argument
            return util.ulocalized_time(time, long_format, self.context,
                                        domain='plonelocales')

    def getFolderishContents(self, folder):
	catalog = getToolByName(self, 'portal_catalog')
	path = folder.getPath()
	if folder.portal_type == "Folder":
		results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, sort_on = 'getObjPositionInParent')
	elif folder.portal_type == "Topic":
		query = folder.getObject().buildQuery()
		if query != None:
			results = catalog.searchResults(query)
		else:
			results = []
	else:
		results = []

	return results
	
    def isVideo(self, item):
	result = IFlowPlayable.providedBy(item)
	if result:
	    print("Item is a video!")
	return result

    def audio_only(self, item):
	result = IAudio.providedBy(item)
	return result
    
    def getValidTypes(self):
	properties_tool = getToolByName(self.context, 'portal_properties', None)
	if properties_tool is not None:
        	references_properties = getattr(properties_tool, 'references_properties', None)
        	if references_properties:
			if references_properties.hasProperty('apply_to'):
				types = references_properties.apply_to
				return types
	return []

    def isValidType(self, type):
	types = self.getValidTypes()
	if type in types:
		return True
	else:
		return False
	    
    def isPublishable(self, item):
	if item.getPortalTypeName() == 'File' or item.getPortalTypeName() == 'Image':
		return False
	else:
		return True

    def getOneWayRelatedItems(self):
        result = []
        try:
            related = self.context.getRefs()
            workflow = getToolByName(self, 'portal_workflow')
            member = getToolByName(self, 'portal_membership')
            
            for item in related:
                if (not self.isPublishable(item) or workflow.getInfoFor(item, 'review_state') == 'published' or not member.isAnonymousUser()):
                    if item.id != self.context.id:
                        result.append(item)
            
            result.append(self.context)
            
            return self.uniq(result)
        except:
            return result

    def getTwoWayRelatedItems(self):
        result = []
        try:
            related = self.context.getRefs()
            workflow = getToolByName(self, 'portal_workflow')
            member = getToolByName(self, 'portal_membership')
            
            for item in related:
                if (not self.isPublishable(item) or workflow.getInfoFor(item, 'review_state') == 'published' or not member.isAnonymousUser()):
                    if item.id != self.context.id:
                        result.append(item)
            
            for backItem in backRelated:
                if (not self.isPublishable(backItem) or workflow.getInfoFor(backItem, 'review_state') == 'published' or not member.isAnonymousUser()):
                    if backItem.id != self.context.id:
                        result.append(backItem)
                        
            return self.uniq(result)
        except:
            return result

    def getRelatedItemsByType(self, type):
	related = self.context.getRefs()
	backRelated = self.context.getBRefs()
	result = []	
	workflow = getToolByName(self, 'portal_workflow')
	member = getToolByName(self, 'portal_membership')
	
	for backItem in backRelated:
		if self.getTypeName(backItem.getPortalTypeName()) == self.getTypeName(type) and (not self.isPublishable(backItem) or workflow.getInfoFor(backItem, 'review_state') == 'published' or not member.isAnonymousUser()):
		#if backItem.getPortalTypeName() == type:
		    if backItem.id != self.context.id:
			result.append(backItem)
	for item in related:
		if self.getTypeName(item.getPortalTypeName()) == self.getTypeName(type) and (not self.isPublishable(item) or workflow.getInfoFor(item, 'review_state') == 'published' or not member.isAnonymousUser()):
		#if item.getPortalTypeName() == type:
		    if item.id != self.context.id:
			result.append(item)
	
	return self.uniq(result)

    def uniq(self, alist):    # Fastest order preserving
        set = {}
        return [set.setdefault(e,e) for e in alist if e not in set]

    def creator(self):
        return self.context.Creator()

    def author(self):
	return 0

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

    def getTypeName(self, type):
	if type == 'Document':
		name = 'Documents'
	elif type == 'Person':
		name = 'People and Organizations'
        elif type == 'Folder':
                name = 'Media'
        elif type == 'Event':
                name = 'Events'
        elif type == 'Work':
                name = 'Works'
        elif type == 'Organization':
                name = 'People and Organizations'
	elif type == 'Image':
		name = 'Image'
	else:
		name = 'Others'	
	
	return name

    def getFolderImages(self, folderItem):
	catalog = getToolByName(self, 'portal_catalog')
	physicalPath = folderItem.getPhysicalPath()
	folderURL = '/'.join(physicalPath)
	catResults = catalog.searchResults(path = {'query' : folderURL,'depth' : 1 }, sort_on = 'getObjPositionInParent', portal_type = ('Image', 'File'))
	results = []
	for item in catResults:
		if (item.portal_type == 'Image') or (item.portal_type == 'File' and IFlowPlayable.providedBy(item.getObject())):
			results.append(item)
	return results  

    def purgeTypes(self, types):
	names = []
	purged = []	

	for item in types:
		if self.getTypeName(item) not in names:
			names.append(self.getTypeName(item))
			purged.append(item)
	return purged

    def getOrderedTypes(self):
	result = ['Event', 'Work', 'Person', 'Organization', 'Document',  'Folder']

	putils = getToolByName(self, 'plone_utils')
	types = putils.getUserFriendlyTypes()

	for item in types:
		if (item not in result):
			result.append(item)

	purgedResult = self.purgeTypes(result)
	
	return purgedResult

    def normalizeString(self, str):
	return self.context.plone_utils.normalizeString(str)

    def hasContentLeadImage(self, obj):
	field = obj.getField(IMAGE_FIELD_NAME)
	if field is not None:
		value = field.get(obj)
	        return not not value
