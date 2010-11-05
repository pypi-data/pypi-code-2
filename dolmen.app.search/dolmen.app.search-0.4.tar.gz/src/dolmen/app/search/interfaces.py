# -*- coding: utf-8 -*-

from zope.schema import Object
from zope.interface import Interface, Attribute, moduleProvides
from zope.catalog.interfaces import ICatalog


class ISearcher(Interface):
    """Defines a component designed to seek and retrieve an element.
    """
    def search(term, *args, **kwargs):
        """Searches elements matching the given term.
        """


class ICatalogSearcher(ISearcher):
    """Defines a specialized searcher using a catalog.
    """
    catalog = Object(
        title = u"Catalog in which the search has to occur.",
        schema = ICatalog,
        required = True
        )

    def search(term, index, permission="zope.View"):
        """Searches a catalog for elements matching the term.
        The searcher can check a given permission on the objects
        of the result set.
        """


class ISearchAPI(Interface):
    """The public Search API.
    """
    ISearcher = Attribute("A component dedicated to search")
    ICatalogSearcher = Attribute("A specialized ISearcher querying a catalog")


moduleProvides(ISearchAPI)
__all__ = list(ISearchAPI)
