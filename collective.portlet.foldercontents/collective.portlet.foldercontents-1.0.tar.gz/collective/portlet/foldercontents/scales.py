from re import compile, search

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

try:
    from plone.app.imaging.utils import getAllowedSizes
except ImportError:
    getAllowedSizes = lambda: {}

from Products.CMFPlone.utils import safe_unicode


class PortalScalesVocabulary(object):
  
    implements(IVocabularyFactory)

    def __call__(self, context):
        # get all scales from properties tool
        try:
            sizes = getAllowedSizes()
        except Exception:
            return SimpleVocabulary([])
        
        # prepare data in required format
        values = []
        for size in sizes.keys():
            width, height = sizes[size]
            values.append({
                'value': safe_unicode(size),
                'title': u'%s (%d:%d)' % (safe_unicode(size), width, height)
            })

        return SimpleVocabulary([SimpleTerm(value['value'], value['value'],
            value['title']) for value in values])
      
PortalScalesVocabularyFactory = PortalScalesVocabulary()
