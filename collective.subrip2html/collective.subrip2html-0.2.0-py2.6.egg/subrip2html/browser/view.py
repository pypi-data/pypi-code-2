# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName 

class SrtView(BrowserView):
    """View file content transformed in SRT"""
    
    @property
    def srt_content(self):
        context = self.context
        pt = getToolByName(context, 'portal_transforms')
        data = context.getFile().data
        if not type(data)==str:
            data = data.data
        html = pt.convert('srt_to_html', data).getData()
        return html
