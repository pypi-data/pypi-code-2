from zope.interface import implements

from zope.schema import Choice
from zope.schema.interfaces import IChoice
                                    
from z3c.i18n.iso import territoryVocabularyFactory

class ICountry(IChoice):
    pass

class Country(Choice):
    """Choice of countries"""
    
    implements(ICountry)
    
    def __init__(self, **kw):
        #kw['vocabulary'] = sortedTerritoryVocabularyFactory(None)
        kw['vocabulary'] = territoryVocabularyFactory(None)
        
        super(Country, self).__init__(**kw)
