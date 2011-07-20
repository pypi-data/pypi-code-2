from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IResponsiveTheme(IDefaultPloneLayer):
    """Marker interface that defines a Zope browser layer.
    """

class IColumnControl(Interface):
    """ """

    def getColumnsClass():
        """ Returns the CSS class based on columns presence. """
        
    def getColumnOneClass():
        """ Returns the CSS class based on columns presence. """
        
    def getColumnTwoClass():
        """ Returns the CSS class based on columns presence. """