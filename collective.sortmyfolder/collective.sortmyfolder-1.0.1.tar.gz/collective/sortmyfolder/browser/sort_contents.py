# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.sortmyfolder import sortFolderMessageFactory as _
from Products.CMFCore.utils import getToolByName

from OFS.interfaces import IOrderedContainer

class SortContentsView(BrowserView):
    """The view for sorting folders"""

    template = ViewPageTemplateFile("sort_contents.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.set('disable_border', True)

    def __call__(self, *args, **kw):
        return self.template()