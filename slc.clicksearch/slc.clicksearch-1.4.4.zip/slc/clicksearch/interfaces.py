from zope import schema
from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer

from slc.clicksearch import ClickSearchMessageFactory as _

class IThemeLayer(Interface):
    """Marker Interface used by BrowserLayer
    """
    
class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """    
    
class ISelectView(Interface):
    """
    """

class IResultView(Interface):
    """ Marker interface for the result snippets
    """

class IClickSearchConfiguration(Interface):
    """This interface defines the configlet
    """
    search_metadata = schema.List(
                        title=_(u"Click Search Metadata"),
                        description=_(u"Specify the available metadata for Click Search portlets"),
                        value_type=schema.Choice(vocabulary="slc.clicksearch.IndexVocabulary"),
                        required=True) 

    sort_indexes = schema.List(
                        title=_(u"Sort on indexes"),
                        description=_(u"Specify the available indexes to sort the clicksearch results by."),
                        value_type=schema.Choice(vocabulary="slc.clicksearch.SortableIndexVocabulary"),
                        required=True) 


