##############################################################################
#
# Copyright (c) 2005-2008 Zope Foundation and Contributors.
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

import sys, os, random, threading
from StringIO import StringIO
from persistent import Persistent
from zope.interface import implements
from hurry.file import interfaces
from zope import component
from zope.app.container.contained import Contained

class HurryFile(Persistent):
    implements(interfaces.IHurryFile)

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
        self.headers = {}

    def _get_file(self):
        storage = component.getUtility(interfaces.IFileRetrieval)
        return storage.getFile(self.data)

    file = property(_get_file)

    @property
    def size(self):
        file = self.file
        if isinstance(file, StringIO):
            return len(file.getvalue())
        else:
            info = os.fstat(file.fileno())
            return info.st_size

    def __eq__(self, other):
        try:
            return (self.filename == other.filename and
                    self.data == other.data)
        except AttributeError:
            return False

    def __ne__(self, other):
        try:
            return (self.filename != other.filename or
                    self.data != other.data)
        except AttributeError:
            return True

def createHurryFile(filename, f):
    retrieval = component.getUtility(interfaces.IFileRetrieval)
    return retrieval.createFile(filename, f)

class IdFileRetrieval(Persistent, Contained):
    """Very basic implementation of FileRetrieval.

    This implementation just returns a File object for the data.
    """
    implements(interfaces.IFileRetrieval)

    def getFile(self, data):
        return StringIO(data)

    def createFile(self, filename, f):
        return HurryFile(filename, f.read())

class TramlineFileRetrievalBase(Persistent, Contained):
    """File retrieval for tramline (base class).
    """
    implements(interfaces.IFileRetrieval)

    def getTramlinePath(self):
        raise NotImplementedError

    def isTramlineEnabled(self):
        return True

    def getFile(self, data):
        # tramline is disabled, so give fall-back behavior for testing
        # without tramline
        if not self.isTramlineEnabled():
            return StringIO(data)
        # we need to retrieve the actual file from the filesystem
        # it could be either a permanently stored file in the repository,
        # or, if that isn't available, potentially a file in the upload
        # directory
        path = self.getTramlinePath()
        if not path:
            raise ValueError("No tramline path configured")
        repository_path = os.path.join(path, 'repository', data)
        try:
            f = open(repository_path, 'rb')
        except IOError:
            upload_path = os.path.join(path, 'upload', data)
            f = open(upload_path, 'rb')
        return f

    def createFile(self, filename, f):
        repository_path = os.path.join(self.getTramlinePath(),
                                       'repository')
        # XXX try to make this thread-safe, but it's not 100% ZEO safe..
        lock = threading.Lock()
        lock.acquire()
        try:
            while True:
                file_id = str(random.randrange(sys.maxint))
                if os.path.exists(os.path.join(repository_path,
                                               file_id)):
                    continue # try again
                break
            path = os.path.join(repository_path, file_id)
            of = open(path, 'wb')
        finally:
            lock.release()

        # XXX this can be made more efficient
        of.write(f.read())
        of.close()

        return HurryFile(filename, file_id)
