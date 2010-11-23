## vocabulary for selecting existing themes

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from ..filesystem import getDirectoriesOfDownloadHome


class ListThemesVocabulary(object):
    """ A vocabulary, that lists existing themes of a given
    filesystem directory. """

    implements(IVocabularyFactory)

    def __call__(self, context):
        """ themes are just subfolders of DOWNLOAD_HOME """
        themes = [SimpleTerm(t) for t in getDirectoriesOfDownloadHome()]
        return SimpleVocabulary(themes)

ListThemesVocabularyFactory = ListThemesVocabulary()
