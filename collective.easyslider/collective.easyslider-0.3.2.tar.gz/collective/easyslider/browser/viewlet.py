from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from collective.easyslider.settings import PageSliderSettings
from collective.easyslider.interfaces import ISliderPage
from base import AbstractSliderView
from plone.memoize.instance import memoize
from Acquisition import aq_inner

class BaseSliderViewlet(ViewletBase):
    
    @memoize
    def get_settings(self):
        return PageSliderSettings(self.context)
    
    settings = property(get_settings)
    
    @memoize
    def get_show(self):
        if not ISliderPage.providedBy(self.context):
            return False
        else:
            if len(self.settings.slides) == 0:
                return False
            else:
                return self.settings.show
                
    show = property(get_show)

class EasySlider(BaseSliderViewlet):

    render = ViewPageTemplateFile('viewlet.pt')
                

class EasySliderHead(BaseSliderViewlet, AbstractSliderView):
    
    render = ViewPageTemplateFile('headviewlet.pt')
    
    