from zope.interface import implements
from zope.component import adapts
from plone.indexer.interfaces import IIndexer

from Products.ZCatalog.interfaces import IZCatalog

from raptus.article.flash.interfaces import IFlash

class Index(object):
    implements(IIndexer)
    adapts(IFlash, IZCatalog)
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        return self.obj.Schema()['components'].get(self.obj)