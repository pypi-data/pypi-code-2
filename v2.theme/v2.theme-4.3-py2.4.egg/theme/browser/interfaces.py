from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "V2 Theme" theme, this interface must be its layer
       (in theme/viewlets/configure.zcml).
    """

class ISearchView(Interface):
    """Used to provide python functions to the search results
    """
    def isVideo(self, item):
	"""Tests if the item is a video
	"""
    def audioOnly(self, item):
        """Test if is audio_only
	"""

    def getSearchableTypes(self):
	"""Organizes search tab types
	"""

    def getTypeName(self, type):
	"""Get the display name (plural) of the type
	"""
    
    def purgeType(self, type):
	""" Converts to plone types ex: Media to Image and File
	"""

    def createSearchURL(self, request, type):
	"""Creates a search URL for the type
	"""
