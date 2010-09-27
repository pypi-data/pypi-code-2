from zope.interface import Interface, Attribute
from zope.schema import Bool, Choice


class IThemeSwitcher(Interface):
    """Marker interface to implement the ThemeSwitcher View. This makes
    ThemeSwitcher local to the Plone site it is installed in. This interface
    is applied to the portal root."""


class ISkinVocabulary(Interface):
    """Skins utiltiy that will return a vocabulary of skin_name
    and interface."""
    
    def getVocab():
        """Vocabulary will be returned via this method from a list of
        sets containing (skin_name, interface)"""


class IThemeSwitcherFormSchema(Interface):
    """A schema to generate a choice (drop-down selection) of themes
    that can be switched to."""
    
    themeswitcher_enable = Bool(
        title=u'Enable/Disable ThemeSwitcher',
        description=u'Select if you want to enable themeswitcher.',
        required=True,
        )
    
    themeswitcher_skin = Choice(
        title=u'Theme Selection',
        default=u'default',
        vocabulary='plone.app.vocabularies.Skins',
        description=u'Select the theme to switch to.',
        required=True
        )

