# -*- coding: utf-8 -*-

#
# Tests for lexicon, splitters, etc.
#

from unittest import TestCase, TestSuite, makeSuite
from Products.ZCTextIndex.Lexicon import Splitter
from Products.ZCTextIndex.Lexicon import CaseNormalizer
from Products.ZCTextIndex.Lexicon import StopWordRemover
from Products.UnicodeLexicon.pipeline import UnicodeWordSplitter
from Products.UnicodeLexicon.pipeline import UnicodeHTMLWordSplitter
from Products.UnicodeLexicon.pipeline import UnicodeCaseNormalizer
from Products.UnicodeLexicon.pipeline import UnicodeSingleCharRemover
from Products.UnicodeLexicon.pipeline import UnicodeStopWordRemover
from Products.UnicodeLexicon.pipeline import UnicodeStopWordAndSingleCharRemover
from Products.UnicodeLexicon.pipeline import UnicodeLatinAccentNormalizer
from Products.UnicodeLexicon.pipeline import UnicodeGermanAccentNormalizer

import locale


class TestLatin1Lexicon(TestCase):

    def afterSetUp(self):
        self._locale = locale.setlocale(locale.LC_ALL)

    def afterClear(self):
        locale.setlocale(locale.LC_ALL, self._locale)

    def testLower(self):
        locale.setlocale(locale.LC_ALL, 'de_DE.ISO8859-15')
        self.assertEqual('K�SSEN'.lower(), 'k�ssen')

    def testLatin1CaseNormalizer(self):
        locale.setlocale(locale.LC_ALL, 'de_DE.ISO8859-15')
        normalize = CaseNormalizer().process
        self.assertEqual(normalize(['�dland']), ['�dland'])

    def testLatin1WordSplitter(self):
        locale.setlocale(locale.LC_ALL, 'de_DE.ISO8859-15')
        split = Splitter().process
        s = 'Sch�ne M�dchen mu� man k�ssen'
        self.assertEqual(split([s]), ['Sch�ne', 'M�dchen', 'mu�', 'man', 'k�ssen'])

    def testLatin1StopWordRemover(self):
        locale.setlocale(locale.LC_ALL, 'de_DE.ISO8859-15')
        remove = StopWordRemover().process
        self.assertEqual(remove(['but', 'M�dchen', 'by', 'and']), ['M�dchen'])


class TestUnicodeLexicon(TestCase):

    def testUnicodeLower(self):
        self.assertEqual(unicode('KÜSSEN', 'utf-8').lower(), u'küssen')

    def testUnicodeCaseNormalizer(self):
        normalize = UnicodeCaseNormalizer().process
        self.assertEqual(normalize(['Ödland']), [u'ödland'])

    def testUnicodeWordSplitter(self):
        split = UnicodeWordSplitter().process
        s = 'Schöne Mädchen muß man küssen'
        self.assertEqual(split([s]), [u'Schöne', u'Mädchen', u'muß', u'man', u'küssen'])

    def testUnicodeHTMLWordSplitter(self):
        split = UnicodeHTMLWordSplitter().process
        s = '&#x26;<title>Schöne</title> Mädchen muß man&nbsp;küssen'
        self.assertEqual(split([s]), [u'Schöne', u'Mädchen', u'muß', u'man', u'küssen'])

    def testUnicodeStopWordRemover(self):
        remove = UnicodeStopWordRemover().process
        self.assertEqual(remove(['but', 'Mädchen', 'by', 'and']), [u'Mädchen'])

    def testUnicodeSingleCharWords(self):
        words = [u'\u03a4', u'\u011f', u'\u9ad8', unicode('Ä', 'utf-8')]
        for w in words:
            self.assertEqual(len(w), 1)

    def testUnicodeSingleCharRemover(self):
        remove = UnicodeSingleCharRemover().process
        self.assertEqual(remove(['\xce\xa4\xce\xb6', 'Mädchen', 'Y', '\xc4\x9f']),
                                [u'\u03a4\u03b6', u'Mädchen'])

    def testUnicodeStopWordAndSingleCharRemover(self):
        remove = UnicodeStopWordAndSingleCharRemover().process
        self.assertEqual(remove(['\xce\xa4\xce\xb6', 'Mädchen', 'Y', '\xc4\x9f', 'by']),
                                [u'\u03a4\u03b6', u'Mädchen'])

    def testUnicodeLatinAccentNormalizer(self):
        normalize = UnicodeLatinAccentNormalizer().process
        self.assertEqual(normalize(['marché']), [u'marche'])
        self.assertEqual(normalize(['voilà']), [u'voila'])
        self.assertEqual(normalize(['muñón']), [u'munon'])
        self.assertEqual(normalize(['pingüino']), [u'pinguino'])
        self.assertEqual(normalize(['Mädchen']), [u'Madchen'])
        self.assertEqual(normalize(['Ödland']), [u'Odland'])

    def testUnicodeGermanAccentNormalizer(self):
        normalize = UnicodeGermanAccentNormalizer().process
        self.assertEqual(normalize(['marché']), [u'marche'])
        self.assertEqual(normalize(['voilà']), [u'voila'])
        self.assertEqual(normalize(['muñón']), [u'munon'])
        self.assertEqual(normalize(['pingüino']), [u'pingüino'])
        self.assertEqual(normalize(['Mädchen']), [u'Mädchen'])
        self.assertEqual(normalize(['Ödland']), [u'Ödland'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestLatin1Lexicon))
    suite.addTest(makeSuite(TestUnicodeLexicon))
    return suite

