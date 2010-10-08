from Products.CMFCore.utils import getToolByName
from republisher import Republisher

def uploadEventHandler(ob, event):
    """Event that fires when an Item changes state"""
    print("uploadEventHandler called for: " + ob.id)
    republisher = Republisher()
    plone_utils = getToolByName(ob, 'plone_utils')
    
    if event.action == 'publish' and ob.id != "cmf_uid" and (ob.portal_type in republisher.allowed_types or plone_utils.isStructuralFolder(ob)):
	itemsAffected = []

	#Get all the contents of the folder of allowed types
	#if is_structural_folder get the contents
	if plone_utils.isStructuralFolder(ob):
	    catalog = getToolByName(ob, 'portal_catalog')
	    folder_url = '/'.join(ob.getPhysicalPath())
	    results = catalog.searchResults(path = {'query' : folder_url, 'depth' : 5 }, sort_on = 'getObjPositionInParent', portal_type = republisher.getAllowedTypes())
	    for item in results:
		itemsAffected.append(item)

	itemsAffected.append(ob)

	#Upload the items images to flickr
	print("Uploading images......")
	for item in itemsAffected:
	   republisher.uploadImageToFlickr(item)
	
	print("image upload finished")
	    
    return

def statelessUploadEventHandler(ob, event):
    """Event that fires when an Item changes state"""
    print("statelessUploadEventHandler called")
    portal_workflow = getToolByName(ob, 'portal_workflow')
    if portal_workflow.getChainForPortalType(ob.portal_type) == (): 
	republisher = Republisher()
	
	print("Uploading image......")
	republisher.uploadImageToFlickr(ob)
	print("image upload finished")
	    
    return