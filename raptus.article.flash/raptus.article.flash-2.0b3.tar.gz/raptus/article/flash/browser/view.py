from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.flash.interfaces import IFlashSize

class View(BrowserView):
    """Flash view
    """
    template = ViewPageTemplateFile('view.pt')
    width = 0
    height = 0
    
    def __call__(self):
        self.width, self.height = IFlashSize(self.context).getSize('full')
        return self.template()
    
    @property
    @memoize
    def url(self):
        return self.context.absolute_url()
