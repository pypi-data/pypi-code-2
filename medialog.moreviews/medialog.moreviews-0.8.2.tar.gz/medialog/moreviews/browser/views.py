from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.app.form import base as ploneformbase
from zope.formlib import form
from collective.easyslider.interfaces import IViewSliderSettings, IPageSliderSettings
from collective.easyslider import easyslider_message_factory as _
from collective.easyslider.settings import PageSliderSettings, ViewSliderSettings
from collective.easyslider.browser.views import SliderView

from collective.easyslider.browser.base import AbstractSliderView
from Acquisition import aq_inner
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.easyslider.utils import slider_settings_css
from Products.ATContentTypes.interface.topic import IATTopic
from Products.ATContentTypes.interface.folder import IATFolder, IATBTreeFolder


class SliderView(BrowserView):
    """
    not sure if this is needed
    """
    
    template = ViewPageTemplateFile('slidercollection.pt')
  
    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)        
        self.settings = ViewSliderSettings(context)
    
    def get_items(self):
        if IATFolder.providedBy(self.context) or IATBTreeFolder.providedBy(self.context):
            res = self.context.getFolderContents(
                contentFilter = {
                    'sort_on' : 'getObjPositionInParent', 
                    'portal_type' : self.settings.allowed_types,
                    'limit' : self.settings.limit 
                }
            )
        elif IATTopic.providedBy(self.context):
            res = aq_inner(self.context).queryCatalog(
                portal_type=self.settings.allowed_types,
                limit=self.settings.limit
            )
            
        if self.settings.limit == 0:
            return res
        else:
            return res[:self.settings.limit]