from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from collective.flowplayer.interfaces import IFlowPlayable
from Products.Archetypes.utils import shasattr

class SearchView(BrowserView):

    def isVideo(self, item):
	result = IFlowPlayable.providedBy(item)
	return result

    def audioOnly(self, item):
	result = IAudio.providedBy(item)
 	return result

    def getSearchableTypes(self):
	ploneTypes = getToolByName(self, 'plone_utils').getUserFriendlyTypes()
	v2Types = ['All', 'Media']
	result = []
	for type in ploneTypes:
		result.append(type)
	for type in v2Types:
		result.append(type)
	
	if 'Image' in result:
		result.remove('Image')
	if 'File' in result:
		result.remove('File')
	
	clean = self.removeBlackListed(result)
	
	order = self.orderTypesList(clean)
	return order 

    def removeBlackListed(self, list):
	blackList = ['Link','News Item', 'Document', 'Favorite', 'Folder', 'FormFolder', 'Large Plone Folder', 'Topic']

	for item in blackList:
		if item in list:
			list.remove(item)
	return list

    def orderTypesList(self, list):
	order = ['All', 'Event', 'Media', 'Organization', 'Person', 'Work']
	result = []

	for type in order:
		if type in list:
			result.append(type)
	for extra in list:
		if extra not in result:
			result.append(extra)
	
	return result

    def purgeType(self, type):
	purgedResult = []

	if type == 'All':
		purgedResult = getToolByName(self, 'plone_utils').getUserFriendlyTypes()
	elif type == 'Media':
		purgedResult = ['File', 'Image']
	else:
		purgedResult = [type]
	
	return purgedResult

    def getTypeName(self, type):
        if type == 'Person':
                name = 'People'
        elif type == 'Event':
                name = 'Events'
        elif type == 'Organization':
                name = 'Organizations'
        elif type == 'Work':
                name = 'Works'
        elif type == 'All':
                name = 'All'
        elif type == 'Media':
                name = 'Media'
        else:
                name = type + 's'

        return name

    def createSearchURL(self, request, type):
	purgedType = self.purgeType(type)
	portal_url = getToolByName(self, 'portal_url')
 
	stext = request.form.get('SearchableText', '')	

	searchURL = portal_url() + '/search?SearchableText=' + stext

	for item in purgedType:
		searchURL += '&portal_type%3Alist=' + item
	
	return searchURL
	
