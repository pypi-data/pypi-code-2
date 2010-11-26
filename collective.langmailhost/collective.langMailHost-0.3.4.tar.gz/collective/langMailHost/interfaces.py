from zope.interface import Interface
from AccessControl import allow_class

class ILangCharset(Interface):
    def lang_charset():
        """Returns lang:charset dictionary from mailhost_properties."""

    def effective_lang():
        """Returns language of member's choice."""

    def effective_charset():
        """Returns charset from the language."""

allow_class(ILangCharset)
