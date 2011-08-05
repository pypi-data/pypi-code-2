##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest
import doctest
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing.placelesssetup import PlacelessSetup

import sqlalchemy
import z3c.zalchemy


singlePrimaryKeyTable = sqlalchemy.Table(
        'singlePrimaryKeyTable',
        z3c.zalchemy.metadata(),
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True),
        sqlalchemy.Column('x', sqlalchemy.Integer),
        )

class SQLTestSingle(object):
    pass

sqlalchemy.mapper(SQLTestSingle, singlePrimaryKeyTable)


multiPrimaryKeyTable = sqlalchemy.Table(
        'multiPrimaryKeyTable',
        z3c.zalchemy.metadata(),
        sqlalchemy.Column('id1', sqlalchemy.Integer, primary_key = True),
        sqlalchemy.Column('id2', sqlalchemy.String,  primary_key = True),
        sqlalchemy.Column('x', sqlalchemy.Integer),
        )

class SQLTestMulti(object):
    def __init__(self, id1, id2):
        self.id1 = id1
        self.id2 = id2

sqlalchemy.mapper(SQLTestMulti, multiPrimaryKeyTable)


def setUp(test):
    setup.placefulSetUp()
    z3c.zalchemy.testing.placefulSetUp(test)
    z3c.zalchemy.createTable('singlePrimaryKeyTable', '')
    z3c.zalchemy.createTable('multiPrimaryKeyTable', '')

def tearDown(test):
    z3c.zalchemy.testing.placefulTearDown(test)
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('../container.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

