
"""
    List the available TagManagers
"""
from zope import component

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ..interfaces import ITagManager

def make_terms(items):
    """ Create zope.schema terms for vocab from tuples,

    @return: Generator of SimpleTerm objects
    """
    terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items ]
    return terms

def vocabulary(context):
    """
        List of available tag managers
    """
    gsm = component.getGlobalSiteManager()
    adapters = [a for a in gsm.registeredAdapters() if a.provided == ITagManager]

    # Return (id, title) pairs
    items = [ (adapter.name, adapter.name) for adapter in adapters ]
    return SimpleVocabulary(make_terms(items))

