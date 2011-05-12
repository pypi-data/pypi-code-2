# -*- coding: utf-8 -*-

from urlparse import urlparse
from zope.interface import implements
from redturtle.video.interfaces import IVideoEmbedCode
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from redturtle.video.browser.videoembedcode import VideoEmbedCode

class ClassicYoutubeEmbedCode(VideoEmbedCode):
    """ ClassicYoutubeEmbedCode 
    Provides a way to have a html code to embed Youtube video in a web page 

    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from redturtle.video.tests.base import TestRequest

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'http://www.youtube.com/watch?v=s43WGi_QZEE&feature=related'
    ...     size = {'width': 425, 'height': 349}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> adapter = getMultiAdapter((remotevideo, TestRequest()), 
    ...                                         IVideoEmbedCode, 
    ...                                         name = 'youtube.com')
    >>> adapter.getVideoLink()
    'http://www.youtube.com/v/s43WGi_QZEE'

    >>> print adapter()
    <object width="425" height="349">
      <param name="movie"
             value="http://www.youtube.com/v/s43WGi_QZEE" />
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <embed src="http://www.youtube.com/v/s43WGi_QZEE"
             type="application/x-shockwave-flash"
             allowscriptaccess="always" allowfullscreen="true"
             width="425" height="349"></embed>
    </object>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('classic_youtubeembedcode_template.pt')

    def getVideoLink(self):
        qs = urlparse(self.context.getRemoteUrl())[4]
        params = qs.split('&')
        for param in params:
            k, v = param.split('=')
            if k == 'v':
                return 'http://www.youtube.com/v/%s' % v


class ShortYoutubeEmbedCode(VideoEmbedCode):
    """ ShortYoutubeEmbedCode 
    Provides a way to have a html code to embed Youtube video in a web page (short way).
    Also, the new version of the embed URL must works:
    
    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from redturtle.video.tests.base import TestRequest

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'http://youtu.be/s43WGi_QZEE'
    ...     size = {'width': 425, 'height': 349}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> adapter = getMultiAdapter((remotevideo, TestRequest()), 
    ...                                         IVideoEmbedCode, 
    ...                                         name = 'youtu.be')
    >>> adapter.getVideoLink()
    'http://youtu.be/s43WGi_QZEE'

    >>> print adapter()
    <object width="425" height="349">
      <param name="movie"
             value="http://www.youtube.com/v/s43WGi_QZEE" />
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <embed src="http://www.youtube.com/v/s43WGi_QZEE"
             type="application/x-shockwave-flash"
             allowscriptaccess="always" allowfullscreen="true"
             width="425" height="349"></embed>
    </object>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('short_youtubeembedcode_template.pt')

    def getEmbedVideoLink(self):
        """Video link, just for embedding needs"""
        path = urlparse(self.context.getRemoteUrl())[2]
        return 'http://www.youtube.com/v%s' % path

    def getVideoLink(self):
        path = urlparse(self.context.getRemoteUrl())[2]
        return 'http://youtu.be%s' % path
