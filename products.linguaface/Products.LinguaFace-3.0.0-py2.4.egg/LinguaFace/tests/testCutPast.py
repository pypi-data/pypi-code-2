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


class TestCut(LinguaFaceTestCase):

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


    def testCutCanonical(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_cutObjects(ids=['doc'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()

        # listB must  be ['doc', 'doc-en', 'doc-es']
        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, [])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        canonicalB = getattr(self.folderB, 'doc')
        englishB = getattr(self.folderB, 'doc-en')
        self.assertEquals(englishB.getCanonical(), canonicalB)

    def testCutTranslation(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_cutObjects(ids=['doc-en'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()

        # listB must  be ['doc', 'doc-en', 'doc-es']
        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, [])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        canonical = getattr(self.folderB, 'doc')
        spanish = getattr(self.folderB, 'doc-es')
        self.assertEquals(spanish.getCanonical(), canonical)



class TestCutNested(LinguaFaceTestCase):

    def afterSetUp(self):

        self.addLanguage('fr')
        self.addLanguage('en')
        self.addLanguage('es')

        self.setLanguage('fr')

        self.folderA = makeContent(self.folder, 'SimpleFolder', 'folderA')
        self.folderB = makeContent(self.folderA, 'SimpleFolder', 'folderB')

        self.french = makeContent(self.folderA, 'SimpleType', 'doc')
        self.french.setLanguage('fr')

        self.english = makeTranslation(self.french, 'en')
        self.spanish = makeTranslation(self.french, 'es')


    def testCutCanonical(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_cutObjects(ids=['doc'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()

        # listB must  be ['doc', 'doc-en', 'doc-es']
        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, ['folderB'])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        canonicalB = getattr(self.folderB, 'doc')
        englishB = getattr(self.folderB, 'doc-en')
        self.assertEquals(englishB.getCanonical(), canonicalB)

    def testCutTranslation(self):
        transaction.savepoint(optimistic=True)
        cp = self.folderA.manage_cutObjects(ids=['doc-en'])
        self.folderB.manage_pasteObjects(cb_copy_data=cp)

        listA = self.folderA.objectIds()

        # listB must  be ['doc', 'doc-en', 'doc-es']
        listB = self.folderB.objectIds()
        listB.sort()

        self.assertEquals(listA, ['folderB'])
        self.assertEquals(listB, ['doc', 'doc-en', 'doc-es'])

        canonicalB = getattr(self.folderB, 'doc')
        englishB = getattr(self.folderB, 'doc-en')
        self.assertEquals(englishB.getCanonical(), canonicalB)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCut))
    suite.addTest(makeSuite(TestCutNested))
    return suite

