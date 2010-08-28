from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.app.form import base as ploneformbase
from zope.formlib import form
from collective.easyslider.interfaces import IViewSliderSettings, IPageSliderSettings
from collective.easyslider import easyslider_message_factory as _
from collective.easyslider.settings import PageSliderSettings, ViewSliderSettings
from base import AbstractSliderView
from Acquisition import aq_inner
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.easyslider.utils import slider_settings_css
from Products.ATContentTypes.interface.topic import IATTopic
from Products.ATContentTypes.interface.folder import IATFolder, IATBTreeFolder

class SliderView(BrowserView, AbstractSliderView):
    
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


class SlidesView(BrowserView):
    """
    View of all the slides
    This uses the same page template as the slides widget--just a different __init__ method
    to setup the call_context and css members
    """
    template = ViewPageTemplateFile('slides.pt')

    def __init__(self, context, request):
        super(SlidesView, self).__init__(context, request)

        self.settings = PageSliderSettings(context.context)
        self.call_context = self.context.context
        self.slider_url = self.context.context.absolute_url()
        self.css = slider_settings_css(self.settings) # since this uses the same .pt file

    def __call__(self):
        return self.template()


class SlideView(BrowserView):
    """
    For doing operations on a slide
    """

    slides_template = ViewPageTemplateFile('slides.pt')

    def __init__(self, context, request):
        super(SlideView, self).__init__(context, request)
        self.settings = PageSliderSettings(self.context.context)
        

    def move_up(self, ajax=None):
        index = self.context.index
        if index > 0:
            slides = self.settings.slides

            tmp = slides[index-1]
            slides[index-1] = slides[index]
            slides[index] = tmp

            self.settings.slides = slides

        if ajax is None:
            self.request.response.redirect(self.context.context.absolute_url() + "/@@slider-settings")
        else:
            return 'done'

    def move_down(self, ajax=None):
        index = self.context.index
        if index < len(self.settings.slides):
            slides = self.settings.slides

            tmp = slides[index+1]
            slides[index+1] = slides[index]
            slides[index] = tmp

            self.settings.slides = slides

        if ajax is None:
            self.request.response.redirect(self.context.context.absolute_url() + "/@@slider-settings")
        else:
            return 'done'

    def remove(self, ajax=None):
        index = self.context.index
        
        if index < len(self.settings.slides) and index >= 0:
            slides = self.settings.slides
            del slides[index]
            self.settings.slides = slides

        if ajax is None:
            self.request.response.redirect(self.context.context.absolute_url() + "/@@slider-settings")
        else:
            return 'done'
