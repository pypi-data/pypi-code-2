
from zope.interface import Interface
from Products.ZCTextIndex.interfaces import ILexicon


class IUnicodeLexicon(ILexicon):
    """Unicode Lexicon for ZCTextIndex"""


class IDefaultEncoding(Interface):
    """The lexicon's default encoding

    To override the default encoding register a utility like so:

    <utility
      provides="Products.UnicodeLexicon.interfaces.IDefaultEncoding"
      component="my.package.pipeline.defaultEncoding"
      />
    """

