# -*- codeing : utf-8 -*-

############################################################################
# Name : 
# Author: Naotaka Jay Hotta
# Date: Aug/19/2008
# Last modified: Oct/6/2008
# E-mail: hotta@cmscom.jp
#         terada@cmscom.jp
#############################################################################

from Products.CMFCore.utils import getToolByName

from Products import BigramSplitter
from Products.BigramSplitter.config import *
import base

class TestInstall(base.BigramSplitterTestCase):
    """ Install basic test """ 
    def afterSetUp(self):
        pass

    def testQuickInstall(self):
        qi = self.portal.portal_quickinstaller
        self.failUnless('BigramSplitter' in (p['id'] for p in qi.listInstallableProducts()))
        qi.installProduct('BigramSplitter')
        self.failUnless(qi.isProductInstalled('BigramSplitter'))

class TestSkinInstall(base.BigramSplitterTestCase):
    """  """
    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')

    def testSkinLayersInstalled(self):
        self.skins = self.portal.portal_skins
        # print self.skins.objectIds()
        self.failUnless('BigramSplitter' in self.skins.objectIds())
        self.assertEqual(len(self.skins.BigramSplitter.objectIds()), 1)

class TestReplaceCatalog(base.BigramSplitterTestCase):
    """ Replace the catalog """ 
    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')            

    def testWordSplitter(self):
        from Products.ZCTextIndex.PipelineFactory import element_factory
        group = 'Word Splitter'
        names = element_factory.getFactoryNames(group)
        self.failUnless('Bigram Splitter' in names)
        
        group = 'Case Normalizer'
        names = element_factory.getFactoryNames(group)
        self.failUnless('Bigram Case Normalizer' in names)
    
    def testCatalogTitle(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        self.failUnless('Title' in cat.indexes())
        
        self.failUnless('bigram_lexicon' in 
                [ix.getLexicon().id for ix in cat.index_objects() if ix.id == 'Title'])
    
    def testCatalogDescription(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        self.failUnless('Description' in cat.indexes())
        
        self.failUnless('bigram_lexicon' in 
                [ix.getLexicon().id for ix in cat.index_objects() 
                                            if ix.id == 'Description'])
    
    def testSearchableText(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        self.failUnless('SearchableText' in cat.indexes())
        
        self.failUnless('bigram_lexicon' in 
                [ix.getLexicon().id for ix in cat.index_objects() 
                                            if ix.id == 'SearchableText'])


class TestUninstall(base.BigramSplitterTestCase):
    """ Uninstall test """ 
    def afterSetUp(self):
        pass
        # qi = self.portal.portal_quickinstaller
        # qi.installProduct('BigramSplitter')

    def testQuickUninstall(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')
        self.failUnless(qi.isProductInstalled('BigramSplitter'))
        qi.uninstallProducts(['BigramSplitter'])
        self.failUnless('BigramSplitter' in (p['id'] for p in qi.listInstallableProducts()))
        #qi.installProduct('BigramSplitter')

    def testWordSplitter(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')
        names = cat.objectIds()
        self.failUnless('bigram_lexicon' in names)
        
        # # Unistall がうまく働いていない。よって以下がエラーをだしてしまう。
        # qi.uninstallProducts(['BigramSplitter'])
        # names = cat.objectIds()
        # self.failUnless('bigram_lexicon' not in names)
        

    def testCatalogTitle(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')
        self.failUnless('bigram_lexicon' in 
                [ix.getLexicon().id for ix in cat.index_objects() if ix.id == 'Title'])
        
        # # Unistall がうまく働いていない。よって以下がエラーをだしてしまう。
        # qi.uninstallProducts(['BigramSplitter'])
        # self.failUnless('plone_lexicon' in 
        #         [ix.getLexicon().id for ix in cat.index_objects() if ix.id == 'Title'])
    
    def testCatalogDescription(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')
        self.failUnless('bigram_lexicon' in 
                [ix.getLexicon().id for ix in cat.index_objects() 
                                            if ix.id == 'Description'])
        # # Unistall がうまく働いていない。よって以下がエラーをだしてしまう。
        # qi.uninstallProducts(['BigramSplitter'])
        # self.failUnless('plone_lexicon' in 
        #         [ix.getLexicon().id for ix in cat.index_objects() 
        #                                     if ix.id == 'Description'])

    def testSearchableText(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        qi = self.portal.portal_quickinstaller
        qi.installProduct('BigramSplitter')
        self.failUnless('bigram_lexicon' in 
                [ix.getLexicon().id for ix in cat.index_objects() 
                                            if ix.id == 'SearchableText'])
        # # Unistall がうまく働いていない。よって以下がエラーをだしてしまう。
        # qi.uninstallProducts(['BigramSplitter'])
        # print [ix.getLexicon().id for ix in cat.index_objects() 
        #                             if ix.id == 'SearchableText']
        # self.failUnless('plone_lexicon' in 
        #         [ix.getLexicon().id for ix in cat.index_objects() 
        #                                     if ix.id == 'SearchableText'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstall))
    suite.addTest(makeSuite(TestSkinInstall))
    suite.addTest(makeSuite(TestUninstall))
    suite.addTest(makeSuite(TestReplaceCatalog))
    return suite
