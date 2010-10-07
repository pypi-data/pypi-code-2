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
"""Interface descriptions"""

import ZEO.ClientStorage
import zope.interface


def RAIDError(message):
    e = RuntimeError(message)
    e.created_by_zeoraid = True
    return e


def RAIDClosedError(message):
    e = ZEO.ClientStorage.ClientStorageError(message)
    e.created_by_zeoraid = True
    return e


class IRAIDStorage(zope.interface.Interface):
    """A ZODB storage providing simple RAID capabilities."""

    def raid_status():
        pass

    def raid_details():
        pass

    def raid_disable(name):
        pass

    def raid_recover(name):
        pass

    def raid_reload():
        pass


class ITransactionInspection(zope.interface.Interface):
    """Storage API extension to allow inspecting historical transactions."""

    def transaction_log(transaction_index, count=1):
        """Return information about `count` transactions starting with the Nth
        transaction given by `transaction_index`.

        Counting starts with the oldest transaction known.

        Return a list of `UndoInfo` records.

        If transactions are requested that do not exist, the returned list may
        be shorter than `count`.

        """

    def transaction_oids(tid):
        """Return a list of OIDs of the objects that were changed in the given
        transaction.
        """
