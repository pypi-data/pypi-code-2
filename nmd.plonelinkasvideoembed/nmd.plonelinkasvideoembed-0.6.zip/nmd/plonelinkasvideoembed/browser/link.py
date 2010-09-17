from p4a.videoembed.interfaces import IVideoMetadataRetriever
from p4a.videoembed.interfaces import IEmbedCodeConverterRegistry

from Products.Five.browser import BrowserView
from zope.component import getUtility
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

try:
    from collective.flowplayer.interfaces import IVideo
    from collective.flowplayer.interfaces import IAudio
    HAS_FLOWPLAYER = True
except ImportError:
    HAS_FLOWPLAYER = False

class VideoLink(BrowserView):
    """ Default view for links with awareness for videos

        Check if the context is a video link from known provider
        or a flowplayer resource.
        If not, just fall back to default view
    """

    index = ViewPageTemplateFile("embed.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.metadata_retriever = getUtility(IVideoMetadataRetriever)
        self.embedcode_converter = getUtility(IEmbedCodeConverterRegistry)

    def metadata(self):
        return self.metadata_retriever.get_metadata(self.context.getRemoteUrl())

    def embedcode(self):
        return self.embedcode_converter.get_code(self.context.getRemoteUrl(), 400)

    @property
    def _view(self):
        traverseview = self.context.aq_inner.restrictedTraverse
        if HAS_FLOWPLAYER and (IVideo.providedBy(self.context) or
                               IAudio.providedBy(self.context)):
            return traverseview('flowplayer')
        elif not self.embedcode():
            return traverseview('link_redirect_view')
        else:
            return self.index

    def __call__(self, *args, **kwargs):
        return self._view()
