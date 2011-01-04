##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import re
import unittest
from transaction.interfaces import IDataManager

import zope.interface
from zope.testing import doctest
from zope.testing import renormalizing
from zope.testing.doctestunit import DocFileSuite


checker = renormalizing.RENormalizing([
    (re.compile('\\\\'), '/'),
    (re.compile('//'), '/'),
    ])

class FailingDataManager(object):
    zope.interface.implements(IDataManager)

    def __init__(self, tm, failon='commit', sortKey=1):
        self.transaction_manager = tm
        self.transaction = tm.get()
        self.failon = failon
        self._sortKey = sortKey

    def failif(self, method):
        if method == self.failon:
            raise ValueError(method)

    def tpc_begin(self, transaction):
        """Begin commit of a transaction, starting the two-phase commit."""
        self.failif('tpc_begin')

    def commit(self, transaction):
        """Commit modifications to registered objects."""
        self.failif('commit')

    def abort(self, transaction):
        """Abort a transaction and forget all changes."""
        self.failif('abort')

    def tpc_finish(self, transaction):
        """Indicate confirmation that the transaction is done."""
        self.failif('tpc_finish')

    def tpc_vote(self, transaction):
        """Verify that a data manager can commit the transaction."""
        self.failif('tpc_vote')

    def tpc_abort(self, transaction):
        """Abort a transaction. This should never fail."""
        self.failif('tpc_abort')

    def sortKey(self):
        return self._sortKey

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
