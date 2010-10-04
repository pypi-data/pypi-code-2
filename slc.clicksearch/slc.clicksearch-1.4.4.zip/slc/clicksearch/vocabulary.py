import re 

from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from Products.CMFCore.utils import getToolByName

from slc.clicksearch.interfaces import IClickSearchConfiguration

class IndexVocabulary(object):
    """Vocabulary factory returning all available indexes.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        pcat = getToolByName(site, 'portal_catalog')
        items = []
        for index in pcat.getIndexObjects():

            # Makes only sense for Keyword and Field indexes
            if index.meta_type not in ['KeywordIndex', 'FieldIndex', 'ProxyIndex']:
                continue
            if index.meta_type == 'ProxyIndex' and index._idx_type not in ['KeywordIndex', 'FieldIndex']:
                continue

            desc = u"%s (%s)" % (
                       index.getId(),
                       index.meta_type
                   )

            items.append(SimpleTerm(index.getId(), index.getId(), desc))
        return SimpleVocabulary(items)

IndexVocabularyFactory = IndexVocabulary()


class SortableIndexVocabulary(object):
    """Vocabulary factory returning all sortable indexes.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        pcat = getToolByName(site, 'portal_catalog')
        items = []
        for index in pcat.getIndexObjects():
            # Make sure it's a sort_on index
            if hasattr(index, 'keyForDocument'):
                title = index.getId().replace('_', ' ')
                pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
                title = pattern.sub(lambda m: m.group()[:1] + " " + m.group()[1:], title)
                title = title.replace('get ', '')
                if title[0].islower():
                    title = title.capitalize()
                title = u"%s (%s)" % (
                        title,
                        index.meta_type
                    )
                items.append(SimpleTerm(index.getId(), index.getId(), title))

        return SimpleVocabulary(items)

SortableIndexVocabularyFactory = SortableIndexVocabulary()

class FilteredIndexVocabulary(object):
    """Vocabulary factory returning filtered indexes.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        settings = getUtility(IClickSearchConfiguration, name='clicksearch_config')
        cat = getToolByName(site, 'portal_catalog')
        items = []
        for i in settings.search_metadata:
            index = cat._catalog.getIndex(i)
            desc = u"%s (%s)" % (
                       index.getId(),
                       index.meta_type
                   )
            items.append(SimpleTerm(index.getId(), index.getId(), desc))
        return SimpleVocabulary(items)

FilteredIndexVocabularyFactory = FilteredIndexVocabulary()

