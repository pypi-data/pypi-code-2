# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class VideoDataViewlet(common.ViewletBase):
    """A viewlet for captions data"""

    render = ViewPageTemplateFile('video_viewlet.pt')
    
    def url(self):
        return self.context.absolute_url()
    
    def captions_url(self):
        return self.context.absolute_url() + '/at_download/captions'