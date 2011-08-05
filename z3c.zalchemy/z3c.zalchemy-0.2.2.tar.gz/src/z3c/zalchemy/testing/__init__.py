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

import transaction
import z3c.zalchemy
from zope.app.testing import setup
from z3c.zalchemy.datamanager import AlchemyEngineUtility
from z3c.zalchemy.interfaces import IAlchemyEngineUtility
from zope import component
import os, tempfile, shutil


def setUp(test):
    pass

def tearDown(test):
    if z3c.zalchemy.inSession():
        try:
            transaction.get().commit()
        except:
            pass
    if _tablesToDrop:
        session = z3c.zalchemy.getSession()
        for table, engine in _tablesToDrop:
            z3c.zalchemy.datamanager.dropTable(table, engine)
        del _tablesToDrop[:]
        transaction.get().commit()
    z3c.zalchemy.datamanager._tableToEngine.clear()
    z3c.zalchemy.datamanager._classToEngine.clear()

def placefulSetUp(test, echo=False):
    setup.placefulSetUp()
    test.tmpDir = tempfile.mkdtemp()
    dbFile = os.path.join(test.tmpDir,'z3c.zalchemy.testing.placefull.db')
    engineUtil = AlchemyEngineUtility(
        'database',
        'sqlite:///%s' % dbFile,
        echo=echo)
    component.provideUtility(engineUtil, IAlchemyEngineUtility)
    test.globs['engineUtil'] = engineUtil

def placefulTearDown(test):
    tearDown(test)
    setup.placefulTearDown()
    shutil.rmtree(test.tmpDir)

_tablesToDrop = []

def dropTable(name, engine=''):
    """Drop table at tearDown.
    """
    _tablesToDrop.append((name, engine))


