##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
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
"""An extended file storage that supports the transaction inspection API."""

import zope.interface

import ZODB.FileStorage

import gocept.zeoraid.interfaces


class FileStorage(ZODB.FileStorage.FileStorage):
    """An extended file storage that supports the transaction inspection API."""

    zope.interface.implements(
        gocept.zeoraid.interfaces.ITransactionInspection)

    def transaction_log(transaction_index, count=1):
        """Return information about `count` transactions starting with the Nth
        transaction given by `transaction_index`.
        """

    def transaction_oids(tid):
        """Return a list of OIDs of the objects that were changed in the given
        transaction.
        """
