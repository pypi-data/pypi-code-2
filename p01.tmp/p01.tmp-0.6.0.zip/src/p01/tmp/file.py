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

import time
import os
import stat
import transaction
from transaction.interfaces import IDataManager

import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty

from p01.tmp import interfaces


class TMPFileTransactionDataManager(object):
    """Transaction Data manager responsible for tmp file cleanup."""

    zope.interface.implements(IDataManager)

    def __init__(self, tmpFile, tm):
        self.timeStamp = time.time()
        self.tmpFile = tmpFile
        self.transaction_manager = tm
        self.transaction = tm.get()
        self.prepared = False

    def tpc_begin(self, transaction):
        """Begin commit of a transaction, starting the two-phase commit."""
        if self.prepared:
            raise TypeError('Already prepared')
        self._checkTransaction(transaction)
        self.prepared = True
        self.transaction = transaction

    def commit(self, transaction):
        """Commit modifications to registered objects."""
        if not self.prepared:
            raise TypeError('Not prepared to commit')
        self._checkTransaction(transaction)
        self.transaction = None
        self.prepared = False

        # remove tmp file
        self.tmpFile.release()

    def abort(self, transaction):
        """Abort a transaction and forget all changes."""
        self.tpc_abort(transaction)

    def tpc_finish(self, transaction):
        """Indicate confirmation that the transaction is done."""
        pass

    def tpc_vote(self, transaction):
        """Verify that a data manager can commit the transaction."""
        return True

    def tpc_abort(self, transaction):
        """Abort a transaction. This should never fail."""
        self._checkTransaction(transaction)
        if self.transaction is not None:
            self.transaction = None
        self.prepared = False

        # remove tmp file
        self.tmpFile.release()

    def sortKey(self):
        return self.timeStamp

    # helpers
    def _checkTransaction(self, transaction):
        """Check for a valid transaction."""
        if (self.transaction is not None and
            self.transaction is not transaction):
            raise TypeError("Transaction mismatch", transaction,
                self.transaction)


class TMPFile(object):
    """Transaction aware temporary file.

    Note: file is a built in type and we can't inherit from built in types
    in python.
    """

    zope.interface.implements(interfaces.ITMPFile)

    _tmpPath = FieldProperty(interfaces.ITMPFile['tmpPath'])

    def __init__(self, name, bufsize=-1):
        self.name = name
        self.bufsize = bufsize
        self._nonzero = False
        # mode MUST BE w+b otherwise it's impossible to read after write!
        # and tempfile.TemporaryFile does the same
        self._v_file = file(self.name, 'w+b', bufsize)
        self._v_len = None

        # now we can set the tmpPath. Later we can set the tmpPath to None if
        # we move the real file to a persistent file system file storage.
        # Every file system file with an existing tmpPath get removed at the
        # end of the transaction.
        self.tmpPath = os.path.abspath(name)

        # apply transaction manager
        tm = transaction.manager
        dm = TMPFileTransactionDataManager(self, tm)
        tm.get().join(dm)

    @property
    def _file(self):
        if not self.closed:
            return self._v_file
        # write once, read often, open the file in read mode
        self._v_file = file(self.name, 'r+b', self.bufsize)
        return self._v_file

    @property
    def ctime(self):
        return int(os.stat(self.name)[stat.ST_CTIME])

    @property
    def atime(self):
        return int(os.stat(self.name)[stat.ST_ATIME])

    def __nonzero__(self):
        return self._nonzero

    def __len__(self):
        return self.size

    # delegated file operations
    def read(self, size=-1):
        return self._file.read(size)

    def close(self):
        if not self.closed:
            self._v_file.close()
        self._v_file = None

    def seek(self, offset, whence=0):
        return self._file.seek(offset, whence)

    def tell(self):
        if self.closed:
            return 0
        return self._file.tell()

    def fileno(self):
        return self._file.fileno()

    def __iter__(self):
        return self._file.__iter__()

    def write(self, s):
        if s:
            self._nonzero = True
        return self._file.write(s)

    def writelines(self, lines):
        return self._file.writelines(lines)

    @property
    def closed(self):
        """like file closed, but lazy"""
        return self._v_file is None or self._v_file.closed

    @apply
    def tmpPath():
        def get(self):
            if os.path.exists(self._tmpPath):
                return self._tmpPath
            else:
                return None
        def set(self, path):
            self._tmpPath = path
        return property(get, set)

    @property
    def size(self):
        if self.tmpPath is not None:
            return int(os.path.getsize(self.tmpPath))
        return 0

    def release(self):
        """Remove the file system file if the file with the tmpPath exist."""
        if self._v_file is not None and not self._v_file.closed:
            self._v_file.close()
        if self.tmpPath is not None:
            os.remove(self._tmpPath)

    def __repr__(self):
        mode = ''
        # prevent to open a closed file
        if not self.closed:
            mode =  " mode='%s'" % self._v_file.mode
        return "<%s at %s%s>" % (self.__class__.__name__, self.name,
            mode)


@zope.interface.implementer(interfaces.ITMPFile)
@zope.component.adapter(None)
def getTMPFile(context):
    """Returns a TMPFile from the TMPStorage for None or any kind of context.

    A custom request can provide it's own adapter which does something else.
    see getTMPFileFactory method
    """
    tmpStorage = zope.component.queryUtility(interfaces.ITMPStorage)
    return tmpStorage.getTMPFile()
