from zope import interface, component
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm

from raptus.article.table.interfaces import IDefinitions

class TableDefinitionsVocabulary(object):
    """ Archetypes vocabulary for table definitions field
    """
    interface.implements(IVocabularyFactory)
    
    def __call__(self, context):
        definitions = IDefinitions(context).getAvailableDefinitions()
        return [SimpleTerm(name, False, definition['name']) for name, definition in definitions.items()]
