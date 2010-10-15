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