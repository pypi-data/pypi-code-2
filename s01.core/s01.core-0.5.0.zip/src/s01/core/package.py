###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""scrapy package installer

$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface

import m01.mongo.item
from m01.mongo.fieldproperty import MongoFieldProperty

from s01.core import interfaces


class ScrapyPackage(m01.mongo.item.MongoStorageItem):
    """ScrapyPackage one per (pkgName, pkgVersion, pyVersion, serverName)"""

    zope.interface.implements(interfaces.IScrapyPackage)

    serverName = MongoFieldProperty(interfaces.IScrapyPackage['serverName'])
    pkgName = MongoFieldProperty(interfaces.IScrapyPackage['pkgName'])
    pkgVersion = MongoFieldProperty(interfaces.IScrapyPackage['pkgVersion'])
    pyVersion = MongoFieldProperty(interfaces.IScrapyPackage['pyVersion'])
    md5Digest = MongoFieldProperty(interfaces.IScrapyPackage['md5Digest'])
    spiderNames = MongoFieldProperty(interfaces.IScrapyPackage['spiderNames'])

    _skipNames = ['__name__']
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified',
                  'serverName', 'pkgName', 'pkgVersion', 'pyVersion',
                  'md5Digest', 'spiderNames',
                 ]

    @property
    def __name__(self):
        return unicode(self._id)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)
