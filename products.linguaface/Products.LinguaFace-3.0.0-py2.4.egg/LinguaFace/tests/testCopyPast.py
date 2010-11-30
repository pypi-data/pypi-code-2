## -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#
# API Tests
#

import transaction

from Products.LinguaPlone.tests.utils import makeContent
from Products.LinguaPlone.tests.utils import makeTranslation

from base import LinguaFaceTestCase


class TestCopy(LinguaFaceTestCase):

    def afterSetUp(self):

        self.addLanguage('fr')
        self.addLanguage('en')
        self.addLanguage('es')

        self.setLanguage('fr')

        self.folderA = makeContent(self.folder, 'SimpleFolder', 'folderA')
        self.folderB = makeContent(self.folder, 'SimpleFolder', 'folderB')

        self.french = makeContent(self.folderA, 'SimpleType', 'doc')
        self.french.setLanguage('fr')

        self.english = makeTranslation(self.french, 'en')
        self.spanish = makeTranslation(self.french, 'es')


    def testCopyCanonical(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_copyObjects(ids=['doc'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()
        listA.sort()

        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, ['doc', 'doc-en', 'doc-es'])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        for folder in [ self.folderA, self.folderB ]:
            canonical = getattr(folder, 'doc')
            self.assertEquals(canonical.isCanonical(), True)
            english = getattr(folder, 'doc-en')
            self.assertEquals(english.getCanonical(), canonical)
            spanish = getattr(folder, 'doc-es')
            self.assertEquals(spanish.getCanonical(), canonical)

    def testCopyTranslation(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_copyObjects(ids=['doc-en'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()
        listA.sort()

        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, ['doc', 'doc-en', 'doc-es'])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        for folder in [ self.folderA, self.folderB ]:
            canonical = getattr(folder, 'doc')
            self.assertEquals(canonical.isCanonical(), True)
            english = getattr(folder, 'doc-en')
            self.assertEquals(english.getCanonical(), canonical)
            spanish = getattr(folder, 'doc-es')
            self.assertEquals(spanish.getCanonical(), canonical)


class TestCopyNested(LinguaFaceTestCase):

    def afterSetUp(self):
        self.addLanguage('fr')
        self.addLanguage('en')
        self.addLanguage('es')
        self.addLanguage('de')

        self.setLanguage('fr')

        self.folderA = makeContent(self.folder, 'SimpleFolder', 'folderA')
        self.folderB = makeContent(self.folderA, 'SimpleFolder', 'folderB')

        self.french = makeContent(self.folderA, 'SimpleType', 'doc')
        self.french.setLanguage('fr')

        self.english = makeTranslation(self.french, 'en')
        self.spanish = makeTranslation(self.french, 'es')


    def testCopyCanonical(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_copyObjects(ids=['doc'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()
        listA.sort()

        # listB must  be ['doc', 'doc-en', 'doc-fr']
        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, ['doc', 'doc-en', 'doc-es', 'folderB'])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        for folder in [ self.folderA, self.folderB ]:
            canonical = getattr(folder, 'doc')
            self.assertEquals(canonical.isCanonical(), True)
            english = getattr(folder, 'doc-en')
            self.assertEquals(english.getCanonical(), canonical)
            spanish = getattr(folder, 'doc-es')
            self.assertEquals(spanish.getCanonical(), canonical)

    def testCopyTranslation(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_copyObjects(ids=['doc-en'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()
        listA.sort()

        # listB must  be ['doc', 'doc-en', 'doc-fr']
        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, ['doc', 'doc-en', 'doc-es', 'folderB'])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        for folder in [ self.folderA, self.folderB ]:
            canonical = getattr(folder, 'doc')
            self.assertEquals(canonical.isCanonical(), True)
            english = getattr(folder, 'doc-en')
            self.assertEquals(english.getCanonical(), canonical)
            spanish = getattr(folder, 'doc-es')
            self.assertEquals(spanish.getCanonical(), canonical)



class TestCopyInSameFolder(LinguaFaceTestCase):

    def afterSetUp(self):

        self.addLanguage('fr')
        self.addLanguage('en')
        self.addLanguage('es')
        self.addLanguage('de')

        self.setLanguage('fr')

        self.french = makeContent(self.folder, 'SimpleType', 'doc')
        self.french.setLanguage('fr')

        self.english = makeTranslation(self.french, 'en')
        self.spanish = makeTranslation(self.french, 'es')

        self.copy_prefix = 'copy_of_'


    def testCopyCanonical(self):
        copies = self.folder.objectIds()
        for id in self.folder.objectIds():
            copies.append(self.copy_prefix + id)
        copies.sort()

        transaction.savepoint(optimistic=True)
        cp = self.folder.manage_copyObjects(ids=['doc'])
        self.folder.manage_pasteObjects(cb_copy_data=cp)

    	listIds = self.folder.objectIds()
    	listIds.sort()

        self.assertEquals(listIds, copies)

        for prefix in [ '', self.copy_prefix ]:
            canonical = getattr(self.folder, '%sdoc' % prefix)
            self.assertEquals(canonical.isCanonical(), True)
            english = getattr(self.folder, '%sdoc-en' % prefix)
            self.assertEquals(english.getCanonical(), canonical)
            spanish = getattr(self.folder, '%sdoc-es' % prefix)
            self.assertEquals(spanish.getCanonical(), canonical)


    def testCopyTranslation(self):
        copies = self.folder.objectIds()
        for id in self.folder.objectIds():
            copies.append(self.copy_prefix + id)
        copies.sort()

        transaction.savepoint(optimistic=True)
        cp = self.folder.manage_copyObjects(ids=['doc-en'])
        self.folder.manage_pasteObjects(cb_copy_data=cp)

    	listIds = self.folder.objectIds()
    	listIds.sort()

        for prefix in [ '', self.copy_prefix ]:
            canonical = getattr(self.folder, '%sdoc' % prefix)
            self.assertEquals(canonical.isCanonical(), True)
            english = getattr(self.folder, '%sdoc-en' % prefix)
            self.assertEquals(english.getCanonical(), canonical)
            spanish = getattr(self.folder, '%sdoc-es' % prefix)
            self.assertEquals(spanish.getCanonical(), canonical)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCopy))
    suite.addTest(makeSuite(TestCopyInSameFolder))
    suite.addTest(makeSuite(TestCopyNested))
    return suite

