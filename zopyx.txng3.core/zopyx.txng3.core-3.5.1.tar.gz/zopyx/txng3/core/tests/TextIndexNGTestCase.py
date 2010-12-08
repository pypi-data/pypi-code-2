###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
TextIndexNG test case

$Id: TextIndexNGTestCase.py 2054 2009-03-14 10:11:29Z ajung $
"""

import unittest

from zope.component.interfaces import IFactory
from zope.app.testing import placelesssetup, ztapi

from zopyx.txng3.core.splitter import SplitterFactory, SimpleSplitterFactory
from zopyx.txng3.core.normalization import Normalizer
from zopyx.txng3.core.stopwords import Stopwords
from zopyx.txng3.core.lexicon import LexiconFactory
from zopyx.txng3.core.storage import StorageFactory
from zopyx.txng3.core.converters.pdf import PDFConverter
from zopyx.txng3.core.parsers.english import EnglishParser
from zopyx.txng3.core.interfaces import IConverter, IStopwords, INormalizer, IParser


class TextIndexNGTestCase(unittest.TestCase):
    """ base test case class for indexer related tests """

    def setUp(self):
        placelesssetup.setUp()
        ztapi.provideUtility(IConverter, PDFConverter, 'application/pdf')
        ztapi.provideUtility(IFactory, SplitterFactory , 'txng.splitters.default')
        ztapi.provideUtility(IFactory, SimpleSplitterFactory , 'txng.splitters.simple')
        ztapi.provideUtility(IParser, EnglishParser(), 'txng.parsers.en')
        ztapi.provideUtility(IFactory, LexiconFactory, 'txng.lexicons.default')
        ztapi.provideUtility(IFactory, StorageFactory, 'txng.storages.default')
        ztapi.provideUtility(IStopwords, Stopwords())
        ztapi.provideUtility(INormalizer, Normalizer())

    def tearDown(self):
        placelesssetup.tearDown()
