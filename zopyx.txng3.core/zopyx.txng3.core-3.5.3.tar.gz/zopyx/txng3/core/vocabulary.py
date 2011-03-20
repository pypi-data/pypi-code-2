###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


"""
Component Vocabularies for the utility-adding view
of the Ting-Index.

Contributed by Frank Burkhardt

$Id: vocabulary.py 2183 2009-07-04 07:59:23Z yvoschu $
"""

import zope.interface

from zopyx.txng3.core.interfaces import ISplitter, ILexicon, IStorage, IParser
try:
    from zope.componentvocabulary.vocabulary import UtilityNames
except ImportError:
    # BBB: old location
    from zope.app.component.vocabulary import UtilityNames
from zope.schema.interfaces import IVocabularyFactory


def SplitterVocabulary(context):
    return UtilityNames(ISplitter)

def LexiconVocabulary(context):
    return UtilityNames(ILexicon)

def StorageVocabulary(context):
    return UtilityNames(IStorage)

def ParserVocabulary(context):
    return UtilityNames(IParser)

zope.interface.directlyProvides(
    SplitterVocabulary, IVocabularyFactory)
zope.interface.directlyProvides(
    LexiconVocabulary, IVocabularyFactory)
zope.interface.directlyProvides(
    StorageVocabulary, IVocabularyFactory)
zope.interface.directlyProvides(
    ParserVocabulary, IVocabularyFactory) 