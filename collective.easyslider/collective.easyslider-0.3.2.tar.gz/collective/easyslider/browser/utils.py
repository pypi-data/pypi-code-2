from zope.interface import implements, alsoProvides, noLongerProvides
from Products.Five.browser import BrowserView
from collective.easyslider.interfaces import *
from Products.CMFCore.utils import getToolByName

try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations


class SliderUtilProtected(BrowserView):
    """
    a protected traverable utility for 
    enabling and disabling sliders
    """
    implements(ISliderUtilProtected)
    def enable(self):
        utils = getToolByName(self.context, 'plone_utils')
        
        if utils.browserDefault(self.context)[1][0] == "sliderview":
            utils.addPortalMessage("You can not add a slider to a page with a Slider view already!")
            self.request.response.redirect(self.context.absolute_url())
        
        elif not ISliderPage.providedBy(self.context):
            alsoProvides(self.context, ISliderPage)
            self.context.reindexObject(idxs=['object_provides'])
            utils.addPortalMessage("You have added a slider to this page. "
                                   " To customize, click the 'Slider Settings' button.")
            self.request.response.redirect(self.context.absolute_url() + '/@@slider-settings')
            
        else:  
            self.request.response.redirect(self.context.absolute_url())
        
    def disable(self):
        utils = getToolByName(self.context, 'plone_utils')
        
        if ISliderPage.providedBy(self.context):
            noLongerProvides(self.context, ISliderPage)
            self.context.reindexObject(idxs=['object_provides'])
            
            #now delete the annotation
            annotations = IAnnotations(self.context)
            metadata = annotations.get('collective.easyslider', None)
            if metadata is not None:
                del annotations['collective.easyslider']
                
            utils.addPortalMessage("Slider removed.")
            
        self.request.response.redirect(self.context.absolute_url())
        
        
class SliderUtil(BrowserView):
    """
    a public traverable utility that checks if a 
    slide is enabled
    """
    implements(ISliderUtil)

    def enabled(self):
        return ISliderPage.providedBy(self.context)    

    def view_enabled(self):
        utils = getToolByName(self.context, 'plone_utils')
        try:
            return utils.browserDefault(self.context)[1][0] == "sliderview"
        except:
            return False

    def should_include(self):
        return self.enabled() or self.view_enabled()
        