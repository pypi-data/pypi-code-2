###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest

import pymongo.objectid

import m01.mongo.testing

import s01.core.interfaces
import s01.core.job
import s01.core.package


# job
class RunSpiderTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return s01.core.interfaces.IRunSpider

    def getTestClass(self):
        return s01.core.job.RunSpider

    def getTestData(self):
        return {'__name__': u'RunSpider'}


class AddPackageTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return s01.core.interfaces.IAddPackage

    def getTestClass(self):
        return s01.core.job.AddPackage

    def getTestData(self):
        return {'__name__': u'AddPackage'}


class SyncPackagesTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return s01.core.interfaces.ISyncPackages

    def getTestClass(self):
        return s01.core.job.SyncPackages

    def getTestData(self):
        return {'__name__': u'RunSpider'}


# package
class ScrapyPackageTest(m01.mongo.testing.MongoItemBaseTest):

    def getTestInterface(self):
        return s01.core.interfaces.IScrapyPackage

    def getTestClass(self):
        return s01.core.package.ScrapyPackage

    def getTestData(self):
        return {'_id': pymongo.objectid.ObjectId()}


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RunSpiderTest),
        unittest.makeSuite(AddPackageTest),
        unittest.makeSuite(SyncPackagesTest),
        unittest.makeSuite(ScrapyPackageTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
