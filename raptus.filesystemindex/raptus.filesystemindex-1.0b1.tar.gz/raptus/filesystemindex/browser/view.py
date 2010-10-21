from zope.interface import implements

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.filesystemindex.interfaces import IFileSystemIndexView

class View(BrowserView):
    implements(IFileSystemIndexView)
    __call__ = ViewPageTemplateFile('view.pt')
    