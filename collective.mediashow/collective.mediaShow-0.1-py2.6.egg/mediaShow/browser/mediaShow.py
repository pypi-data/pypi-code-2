from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class GetMediaShowItemView(BrowserView):
    """ Class that extracts relevant information for the slideshow
    """
    def getJSON(self):
        callback = hasattr(self.request, 'callback') and 'json' + self.request['callback'] or None
        
        media = self.getMediaURL()
        mediaType = self.getMediaType()
        
        if hasattr(self.context, "title"):
            title = self.context.title
        elif hasattr(self.context, "Title"):
            title = self.context.Title()
        else:
            title = ""
        
        if hasattr(self.context, "description"):
            description = self.context.description
        elif hasattr(self.context, "Description"):
            description = self.context.Description()
        else:
            description = ""
           
        type = self.context.portal_type
            
        title = self.sanitizeStringForJson(title)    
        description = self.sanitizeStringForJson(description)
        
        #print(description)
            
        jsonStr = '{"title": "'+title+'", "description": "'+description+'", "type": "'+type+'", "media": {"url": "'+media+'", "type" : "'+mediaType+'"}}'
        if callback is not None:
            return callback +'(' + jsonStr + ')'
        else:
            return jsonStr
        
    def sanitizeStringForJson(self, str):
        str = str.replace("\n", " ").replace('"', '\\"');
        return str
     
    def getMediaURL(self):
        """ finds and returns relevant leading media for the context item
        """
        item = self.context     
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if plone_utils.isStructuralFolder(item):
            results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, type = 'Image', sort_on = 'getObjPositionInParent')
            if len(results) > 0:
                leadMedia = results[0]
                if leadMedia.portal_type == 'Image':
                    return leadMedia.getURL() + '/image_large'
                else:
                    return leadMedia.getURL()
            else:
                return ""
        else:
            #TODO: Add lead image support and News Item Image support
            return ""
        
    def getMediaType(self):
        """ Finds and returns the type of lead image
        """
        return "Image"
    
    
class MediaShowListingView(BrowserView):
    """ Class that extracts relevant information for the slideshow
    """
    
    def getJSON(self):
        callback = hasattr(self.request, 'callback') and 'json' + self.request['callback'] or None
        jsonStr = ""
        
        item = self.context     
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if item.portal_type == "Folder":
            results = catalog.searchResults(path = { 'query' : path, 'depth' : 1 }, sort_on = 'getObjPositionInParent')
        elif item.portal_type == "Topic":
            results = catalog.searchResults(item.getQuery())
        else:
            results = []
            
        jsonStr = "["
        for res in results:
            if(self.getMediaURL(res.getObject()) != ""):
                jsonStr += '"'+res.getURL()+'"'
                jsonStr += ","
            
        if jsonStr != "[":
            jsonStr = jsonStr[:-1]
        jsonStr += "]"
        
        if callback is not None:
            return callback +'(' + jsonStr + ')'
        else:
            return jsonStr 
        
        
    def getMediaURL(self, item):
        """ finds and returns relevant leading media for the given item
        """    
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if plone_utils.isStructuralFolder(item):
            results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, type = 'Image', sort_on = 'getObjPositionInParent')
            if len(results) > 0:
                leadMedia = results[0]
                if leadMedia.portal_type == 'Image':
                    return leadMedia.getURL() + '/image_large'
                else:
                    return leadMedia.getURL()
            else:
                return ""
        else:
            #TODO: Add lead image support and News Item Image support
            return ""