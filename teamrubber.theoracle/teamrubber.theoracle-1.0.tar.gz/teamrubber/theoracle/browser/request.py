from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements

class Request(BrowserView):
    implements(ICategory)
    title = "Request"