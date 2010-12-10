import os.path
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

# check:
# how to work with pkg_resources Requirement classes
# how to work with pkg_resources split packages, e.g. those using namespace_packages
# how will this play along distutils2 and its pkgutil.open()
# support unicode/encodings/etc.

import os

from pydenji.pathtools import verify_path_existence
from pydenji.uriresolver import resource_filename_resolver

class ResourceAccessError(IOError):
    pass

class RWResource(object):
    _resolver = staticmethod(resource_filename_resolver)

    def __init__(self, uri, mode):
        self.filename = self._resolver(uri)
        self._mode = mode
        self._verify_consistency()

    def _verify_consistency(self):
        # template method, should raise an exception
        # if something is wrong.
        pass


    def open(self, buffering=-1):
        return open(self.filename, self._mode, buffering)


class ReadResource(RWResource):
    def __init__(self, uri, binary=False):
        super(ReadResource, self).__init__(
            uri, "r" + ("b" if binary else "") )

    def _verify_consistency(self):
        verify_path_existence(self.filename, ResourceAccessError)
        if not os.access(self.filename, os.R_OK):
            raise ResourceAccessError, ("Insufficient privileges, "
                "can't read '%s' " % self.filename)

class WriteResource(RWResource):
    def _verify_consistency(self):
        write_path_dir, basename = os.path.split(self.filename)
        verify_path_existence(write_path_dir, ResourceAccessError)
        if not os.path.isdir(write_path_dir):
            raise ResourceAccessError, "'%s' is not a directory, can't write '%s'" % (
                write_path_dir, basename)
        if not os.access(write_path_dir, os.W_OK):
            raise ResourceAccessError, ("Insufficient privileges, "
                "can't write '%s' in '%s' " % (basename, write_path_dir))
        if os.path.exists(self.filename) and not os.access(self.filename, os.W_OK):
            raise ResourceAccessError, ("Insufficient privileges, can't overwrite '%s'" %
                self.filename)

def OverwritingWriteResource(uri, binary=False):
    return WriteResource(uri, "w" + ("b" if binary else ""))

def AppendingWriteResource(uri, binary=False):
    # TODO: do we need an appender which just appends, e.g. never creates?
    return WriteResource(uri, "a" + ("b" if binary else ""))

class NewFileWriteResource(WriteResource):
    def __init__(self, uri, binary=False):
        super(NewFileWriteResource, self).__init__(uri, "w" + ("b" if binary else ""))
        
    def _verify_consistency(self):
        if os.path.exists(self.filename):
            raise ResourceAccessError, "'%s' already exists." % self.filename
        super(NewFileWriteResource, self)._verify_consistency()

class ExecutableResource(object):
    _resolver = staticmethod(resource_filename_resolver)

    def __init__(self, uri):
        self.filename = self._resolver(uri)
        self._verify_consistency()

    def _verify_consistency(self):
        verify_path_existence(self.filename, ResourceAccessError)
        if not os.access(self.filename, os.X_OK):
            raise ResourceAccessError, ("Insufficient privileges, "
                "can't execute '%s' " % self.filename)

def enumerateResources(resource, childrenResourceFactory=ReadResource):
    # this is a bit naive, but we probably won't need anything more.
    if os.path.isdir(resource.filename):
        return [childrenResourceFactory(resource.filename + os.sep + path) for
            path in os.listdir(resource.filename)]
    else:
        return [childrenResourceFactory(resource.filename)]
            