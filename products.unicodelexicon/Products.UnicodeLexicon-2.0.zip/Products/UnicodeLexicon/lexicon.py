
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import DTMLFile

from Products.ZCTextIndex import ZCTextIndex

from zope.interface import implements
from interfaces import IUnicodeLexicon

from pipelinefactory import element_factory

from pipeline import UnicodeWordSplitter
from pipeline import UnicodeHTMLWordSplitter
from pipeline import UnicodeCaseNormalizer
from pipeline import UnicodeStopWordRemover
from pipeline import UnicodeSingleCharRemover
from pipeline import UnicodeStopWordAndSingleCharRemover
from pipeline import UnicodeLatinAccentNormalizer
from pipeline import UnicodeGermanAccentNormalizer


element_factory.registerFactory('Word Splitter',
                                'Whitespace splitter',
                                UnicodeWordSplitter)

element_factory.registerFactory('Word Splitter',
                                'HTML aware splitter',
                                UnicodeHTMLWordSplitter)

element_factory.registerFactory('Case Normalizer',
                                'Case normalizer',
                                UnicodeCaseNormalizer)

element_factory.registerFactory('Stop Words',
                                'Don\'t remove stop words',
                                None)

element_factory.registerFactory('Stop Words',
                                'Remove stop words',
                                UnicodeStopWordRemover)

element_factory.registerFactory('Stop Words',
                                'Remove single char words',
                                UnicodeSingleCharRemover)

element_factory.registerFactory('Stop Words',
                                'Remove stop words and single char words',
                                UnicodeStopWordAndSingleCharRemover)

element_factory.registerFactory('Accent Normalizer',
                                'Don\'t normalize accented chars',
                                None)

element_factory.registerFactory('Accent Normalizer',
                                'Normalize accented chars (Latin & Western European text)',
                                UnicodeLatinAccentNormalizer)

element_factory.registerFactory('Accent Normalizer',
                                'Normalize accented chars (German & Scandinavian text)',
                                UnicodeGermanAccentNormalizer)


class UnicodeLexicon(ZCTextIndex.PLexicon):
    """Unicode Lexicon for ZCTextIndex"""

    implements(IUnicodeLexicon)

    meta_type = 'ZCTextIndex Unicode Lexicon'

    security = ClassSecurityInfo()

InitializeClass(UnicodeLexicon)


manage_addLexiconForm = DTMLFile('www/addLexicon', globals())

def manage_addLexicon(self, id, title='', elements=[], REQUEST=None):
    """Add ZCTextIndex Unicode Lexicon"""

    pipeline = []
    for el_record in elements:
        if not hasattr(el_record, 'name'):
            continue # Skip over records that only specify element group
        element = element_factory.instantiate(el_record.group, el_record.name)
        if element is not None:
            pipeline.append(element)

    lexicon = UnicodeLexicon(id, title, *pipeline)
    self._setObject(id, lexicon)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

