#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from urlparse import urlparse
from pkg_resources import resource_filename

def file_uri_resolver(parsed_uri):
    if not parsed_uri.path.startswith("/"):
        raise ValueError, "Relative paths are not supported."
    if parsed_uri.netloc:
        raise ValueError, "Netloc in file scheme is unsupported."
    return parsed_uri.path

def package_uri_resolver(parsed_uri):
    return resource_filename(parsed_uri.netloc, parsed_uri.path)

supported_schemes = {
    "file" : file_uri_resolver,
    "" : file_uri_resolver,
    "pkg": package_uri_resolver,
}

def resource_filename_resolver(resource_uri):
    parsed = urlparse(resource_uri)
    if parsed.scheme not in supported_schemes:
        raise TypeError, "Scheme '%s' is unsupported" % parsed.scheme
    return supported_schemes[parsed.scheme](parsed)
