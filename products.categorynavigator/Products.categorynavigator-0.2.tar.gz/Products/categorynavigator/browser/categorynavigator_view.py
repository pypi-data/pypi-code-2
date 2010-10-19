from Products.Five import BrowserView
from Products.categorynavigator.categoryutils import CategoryUtils
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot


try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    LEADIMAGE_EXISTS = True
except ImportException:
    LEADIMAGE_EXISTS = False
    

class CategoryNavigatorView(BrowserView, CategoryUtils):
    '''view class for the Category Navigator'''
    
    def leadImageInstalled(self):
        return LEADIMAGE_EXISTS
    
    def getDescriptionOrBobySegment(self, item):
        '''Returns a description of the item or, if it does not exist, the first 240 characters of the body'''
        if item.Description == "":
            return self.trimDescription(item.getObject().getText(), 240 )
        else:
            return item.Description
    
    def trimDescription(self, desc, num):
        if len(desc) > num: 
                res = desc[0:num]
                lastspace = res.rfind(" ")
                res = res[0:lastspace] + " ..."
                return res
        else:
                return desc

    def getUrlWithQueryString(self, item, categories):
        url = ""
        if hasattr(item, 'getURL'):
            url = item.getURL()
        else:
            url = item.absolute_url()
        
        url = url + self.generateQueryString(categories)
        return url
        
    def getAllResultsHere(self, context):
        '''Malkes the search for all the items in this folder'''
        catalog = self.tools().catalog()
        folder_path = '/'.join(context.getPhysicalPath())
        types = ('Document', 'Event', 'News Item')
        results = catalog.searchResults(path={'query': folder_path, 'depth': 1}, portal_type=types, batch=True)
        return results
    
    @property
    def prefs(self):
        if LEADIMAGE_EXISTS:
            portal = getUtility(IPloneSiteRoot)
            return ILeadImagePrefsForm(portal)
        else:
            return None

    def tag(self, obj, css_class='tileImage'):
        if LEADIMAGE_EXISTS:
            context = aq_inner(obj)
            field = context.getField(IMAGE_FIELD_NAME)
            if field is not None:
                if field.get_size(context) != 0:
                    scale = self.prefs.desc_scale_name
                    return field.tag(context, scale=scale, css_class=css_class)
            return ''
        else:
            return ''