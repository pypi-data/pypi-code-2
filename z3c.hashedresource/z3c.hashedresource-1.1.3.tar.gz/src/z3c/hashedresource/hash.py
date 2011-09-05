#############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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

from z3c.hashedresource import interfaces
from zope.interface import implements, implementsOnly
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
import os


class ContentsHash(object):

    implements(interfaces.IResourceContentsHash)

    def __init__(self, context):
        self.context = context

    def __str__(self):
        path = self.context.context.path
        if os.path.isdir(path):
            files = self._list_directory(path)
        else:
            files = [path]

        result = md5()
        for file in files:
            f = open(file, 'rb')
            data = f.read()
            f.close()
            result.update(data)
        result = result.hexdigest()
        return result

    def _list_directory(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                yield os.path.join(root, file)


_contents_hash = {}

class CachingContentsHash(ContentsHash):

    def __str__(self):
        path = self.context.context.path
        try:
            return _contents_hash[path]
        except KeyError:
            result = super(CachingContentsHash, self).__str__()
            _contents_hash[path] = result
            return result
