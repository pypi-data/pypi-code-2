from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope browser layer.
    """

class IPersonalizeFormValidators(Interface):
    """An simple interface to implement validators
    """

