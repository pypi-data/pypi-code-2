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
"""Unit test support."""

import ZODB.FileStorage
import ZODB.config
import tempfile
import zope.proxy


class Opener(ZODB.config.BaseConfig):

    def open(self):
        blob_dir = self.config.blob_dir
        if blob_dir is None:
            blob_dir = tempfile.mkdtemp()
        file_handle, file_name = tempfile.mkstemp()
        fs = ZODB.FileStorage.FileStorage(file_name)
        return FailingStorage(blob_dir, fs)


def failing_method(name):
    """Produces a method that can be made to fail."""
    def fail(self, *args, **kw):
        if name == self._fail:
            self._fail = None
            raise Exception()
        if hasattr(ZODB.blob.BlobStorage, name):
            original_method = getattr(ZODB.blob.BlobStorage, name).fget(self)
        else:
            original_method = getattr(zope.proxy.getProxiedObject(self), name)
        return original_method(*args, **kw)
    return fail


class FailingStorage(ZODB.blob.BlobStorage):

    __slots__ = ('_fail',) + ZODB.blob.BlobStorage.__slots__

    def __init__(self, base_directory, storage):
        ZODB.blob.BlobStorage.__init__(
            self, base_directory, storage)
        self._fail = None

    @zope.proxy.non_overridable
    def close(self):
        if self._fail == 'open':
            self._fail = None
            raise Exception()
        zope.proxy.getProxiedObject(self).close()
        zope.proxy.getProxiedObject(self).cleanup()
        # XXX rmtree blobdir

    @zope.proxy.non_overridable
    def getExtensionMethods(self):
        return dict(fail=None)

    # Create a set of stub methods that have to be made to fail but are set as
    # non-data descriptors on the proxy object.
    __stub_methods__ = ['history', 'loadSerial', 'close', 'getSize', 'pack',
                        'tpc_abort', 'tpc_finish', 'storeBlob', 'loadBlob',
                        'undo', 'record_iternext', 'getTid']
    for name in __stub_methods__:
        method = zope.proxy.non_overridable(failing_method(name))
        locals()[name] = method

    @zope.proxy.non_overridable
    def fail(self, method_name):
        if method_name in self.__stub_methods__:
            # Those methods are copied/references by the server code, we can't
            # rebind them here.
            self._fail = method_name
            return

        old_method = getattr(self, method_name)
        def failing_method(*args, **kw):
            setattr(self, method_name, old_method)
            raise Exception()
        setattr(self, method_name, failing_method)
