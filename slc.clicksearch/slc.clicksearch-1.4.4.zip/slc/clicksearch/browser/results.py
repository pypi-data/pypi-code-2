from zope.interface import implements, Interface
from slc.clicksearch.interfaces import IResultView
from plone.app.layout.icons.interfaces import IContentIcon
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from slc.clicksearch.util import current_query
from slc.clicksearch.browser.clicksearch import ClickSearchView

try:
    from p4a.video.interfaces import IVideo, IVideoEnhanced
    from p4a.plonevideoembed.interfaces import IVideoLinkEnhanced
    from p4a.fileimage.image._widget import ImageURLWidget
    from p4a.video.browser.video import VideoListedSingle
except ImportError:
    class IVideoEnhanced(Interface):
        """ Dummy interface if p4a.video is not installed """
    class IVideoLinkEnhanced(Interface):
        """ Dummy interface if p4a.video is not installed """

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SimpleResultView(ClickSearchView):
    """ Generic result view
    """
    implements(IResultView)
    
    template = ViewPageTemplateFile('templates/simple_result.pt')
    
    def __call__(self, result):
        self.result = result
        self.query = current_query(self.request)

        self.result_url = result.getURL()
        self.plone_view = self.context.restrictedTraverse('@@plone')
        self.site_properties = getToolByName(self.context, 'portal_properties').site_properties
        pm = getToolByName(self.context, 'portal_membership')
        self.isAnon = pm.isAnonymousUser()
        self.portal_url = getToolByName(self.context, 'portal_url')()
        self.searchterm = getattr(self.request, 'SearchableText', '')
        return self.template()


class FileResultView(ClickSearchView):
    """ File result view
        Special handling of p4a video
    """
    implements(IResultView)
    
    template = ViewPageTemplateFile('templates/simple_result.pt')
    
    def __call__(self, result):
        self.result = result
        self.query = current_query(self.request)
        
        
        self.is_video = False
        ob = result.getObject()
        if IVideoEnhanced.providedBy(ob):
            videoobj = IVideo(ob)
            #import pdb; pdb.set_trace()
            #image_field = IVideo['video_image'].bind(videoobj)
            #self.image_widget = ImageURLWidget(image_field, self.request)
            #self.has_image = True
            self.videoobj = videoobj
            dumb_view = VideoListedSingle(self.context, self.request)
            self.video = dumb_view.safe_video(obj=videoobj)
            self.template = ViewPageTemplateFile('templates/video_result.pt')

        self.result_url = result.getURL()
        self.plone_view = self.context.restrictedTraverse('@@plone')
        self.site_properties = getToolByName(self.context, 'portal_properties').site_properties
        pm = getToolByName(self.context, 'portal_membership')
        self.isAnon = pm.isAnonymousUser()
        self.portal_url = getToolByName(self.context, 'portal_url')()
        self.searchterm = getattr(self.request, 'SearchableText', '')
        return self.template()

class LinkResultView(ClickSearchView):
    """ Link result view
        Special handling of p4a video
    """
    def __call__(self, result):
        self.result = result
        self.query = current_query(self.request)
        
        
        self.is_video = False
        ob = result.getObject()
        if IVideoLinkEnhanced.providedBy(ob):
            videoobj = IVideo(ob)
            self.videoobj = videoobj
            dumb_view = VideoListedSingle(self.context, self.request)
            self.video = dumb_view.safe_video(obj=videoobj)
            self.template = ViewPageTemplateFile('templates/video_result.pt')

        self.result_url = result.getURL()
        self.plone_view = self.context.restrictedTraverse('@@plone')
        self.site_properties = getToolByName(self.context, 'portal_properties').site_properties
        pm = getToolByName(self.context, 'portal_membership')
        self.isAnon = pm.isAnonymousUser()
        self.portal_url = getToolByName(self.context, 'portal_url')()
        self.searchterm = getattr(self.request, 'SearchableText', '')
        return self.template()
