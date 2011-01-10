from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer

class IThemeItalianSkin(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IValidatorView(Interface):
    """ Validator info """

    def validateURL():
        """ Returns the validation url """
