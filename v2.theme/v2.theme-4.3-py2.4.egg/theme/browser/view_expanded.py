import time
import string
from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from collective.flowplayer.interfaces import IFlowPlayable
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IAudio

class ExpandedView(BrowserView):
    
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class)
        return ''

    def currenttime(self):
	return time.time()
    
    def trimDescription(self, desc):
	if len(desc) > 250: 
		res = desc[0:250]
		lastspace = res.rfind(" ")
		res = res[0:lastspace] + " ..."
		return res
	else:
		return desc

    def isPublishable(self, item):
	if item.getPortalTypeName() == 'File' or item.getPortalTypeName() == 'Image':
		return False
	else:
		return True

    def getRelatedItemsByType(self, type):
	related = self.context.getRefs()
	backRelated = self.context.getBRefs()
	result = []	
	workflow = getToolByName(self, 'portal_workflow')
	member = getToolByName(self, 'portal_membership')
	
	for backItem in backRelated:
		if self.getTypeName(backItem.getPortalTypeName()) == self.getTypeName(type) and (not self.isPublishable(backItem) or workflow.getInfoFor(backItem, 'review_state') == 'published' or not member.isAnonymousUser()):
		#if backItem.getPortalTypeName() == type:
			result.append(backItem)
	for item in related:
		if self.getTypeName(item.getPortalTypeName()) == self.getTypeName(type) and (not self.isPublishable(item) or workflow.getInfoFor(item, 'review_state') == 'published' or not member.isAnonymousUser()):
		#if item.getPortalTypeName() == type:
			result.append(item)
	
	return self.uniq(result)

    def uniq(self, alist):    # Fastest order preserving
        set = {}
        return [set.setdefault(e,e) for e in alist if e not in set]
	

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

    def isVideo(self, item):
        result = IFlowPlayable.providedBy(item)
        return result

    def audio_only(self, item):
        result = IAudio.providedBy(item)
        return result	

    def getOrderedTypes(self):
	result = ['Event', 'Work', 'Person', 'Organization', 'Document',  'Folder']

	putils = getToolByName(self, 'plone_utils')
	types = putils.getUserFriendlyTypes()

	for item in types:
		if (item not in result):
			result.append(item)

	purgedResult = self.purgeTypes(result)
	
	return purgedResult
