#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

# TBD: something to get consistent access to resources, just like
# springs own classpath/file/url etc. parser.
# check:
# how to work with pkg_resources Requirement classes
# how to work with pkg_resources split packages, e.g. those using namespace_packages
# how will this play along distutils2 and its pkgutil.open()

import os
from urlparse import urlparse

from pkg_resources import resource_filename
from pydenji.pathtools import verify_path_existence


# this currently more a resourcelocator than a resourceloader. 

# do we need this?
class Resource(object):

    # will the stream be open for reading or for writing?
    # by default I think we'll just support reading streams.
    # binary or not?
    # too complex?
    # check what Spring does.
    def get_stream(self, mode):
        raise NotImplementedError, "Not yet implemented."

    @property
    def filename(self):
        raise NotImplementedError, "Not yet implemented."

def file_uri_resolver(parsed_uri):
    if not parsed_uri.path.startswith("/"):
        raise ValueError, "Relative paths are not supported."
    if parsed_uri.netloc:
        raise ValueError, "Netloc in file scheme is unsupported."
    return parsed_uri.path

def package_uri_resolver(parsed_uri):
    return resource_filename(parsed_uri.netloc, parsed_uri.path)

# todo: support hooks for different schemes?
supported_schemes = {
    "file" : file_uri_resolver,
    "pkg": package_uri_resolver,
}

# should it break if resource does not exist?
# maybe optionally? a differenct factory? readresourceloader, writeresourceloader,
# mayberesourceloader?
# check: filepath is always absolute?
def resource_filename_resolver(resource_uri):
    # TODO: add a default resolver for un-uried resources?
    
    parsed = urlparse(resource_uri)
    if parsed.scheme not in supported_schemes:
        raise TypeError, "Scheme '%s' is unsupported" % parsed.scheme

    return supported_schemes[parsed.scheme](parsed)

class Resource(object):
    # TODO: check whether twisted filepath is better.
    _resolver = staticmethod(resource_filename_resolver)

    def __init__(self, uri, mode):
        self.filename = self._resolver(uri)
        self._mode = mode
        self._verify_consistency()

    def _verify_consistency(self):
        # template method, should raise an exception
        # if something is wrong.
        pass

    def stream(self):
        return open(self.filename, self._mode)



class ReadResource(Resource):
    def __init__(self, uri, binary=False):
        super(ReadResource, self).__init__(
            uri, "r" + ("b" if binary else "") )

    def _verify_consistency(self):
        verify_path_existence(self.filename)
        if not os.access(self.filename, os.R_OK):
            raise ValueError, ("Insufficient privileges, "
                "can't read '%s' " % self.filename)

class WriteResource(Resource):

    def _verify_consistency(self):
        write_path_dir, basename = os.path.split(self.filename)
        verify_path_existence(write_path_dir)
        if not os.path.isdir(write_path_dir):
            raise ValueError, "'%s' is not a directory, can't write '%s'" % (
                write_path_dir, basename)
        if not os.access(write_path_dir, os.W_OK):
            raise ValueError, ("Insufficient privileges, "
                "can't write '%s' in '%s' " % (basename, write_path_dir))
        if os.path.exists(self.filename) and not os.access(self.filename, os.W_OK):
            raise ValueError, ("Insufficient privileges, can't overwrite '%s'" %
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
            raise ValueError, "'%s' already exists." % self.filename
        super(NewFileWriteResource, self)._verify_consistency()


 









    


