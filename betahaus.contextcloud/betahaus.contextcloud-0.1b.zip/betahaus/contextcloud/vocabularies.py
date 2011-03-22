from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName

from betahaus.contextcloud import ContextCloudMessageFactory as _


class SelectableCatalogIndexes(object):
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        context = getattr(context, 'context', context) #Uhm... Well
        catalog = getToolByName(context, 'portal_catalog', None)
        if catalog is None:
            return None
        
        portal_props = getToolByName(context, 'portal_properties')
        #If this doesn't work, we do want an attribute error!
        ignore_columns = portal_props.contextcloud.ignore_columns
        
        #schema in the catalog represents the columns
        indexes = set([x for x in catalog.schema() if x not in ignore_columns])
        
        #We'll want to walk through the indexes to make sure they're either
        #a KeywordIndex or FieldIndex. Using a DateTimeIndex with a facet wouldn't make sense
        for index in indexes.copy(): #Otherwise we can't change it
            #Does the index exist?
            catindex = catalog.Indexes.get(index)
            if catindex is None:
                indexes.remove(index)
                continue
            if catindex.meta_type not in ['FieldIndex', 'KeywordIndex']:
                indexes.remove(index)
        
        #Ahem, isn't there a better way to do this? This seems insane.
        return SimpleVocabulary([SimpleTerm(x, title=x) for x in indexes])

SelectableCatalogIndexesFactory = SelectableCatalogIndexes()


class SelectableLayouts(object):
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        layouts = (('cloud', _(u"Tag cloud")),
                   ('list', _(u"List with numbers")),
                   )
        return SimpleVocabulary([SimpleTerm(x[0], title=x[1]) for x in layouts])

SelectableLayoutsFactory = SelectableLayouts()