##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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

import zope.schema
import m01.mongo.interfaces
import m01.mongo.schema
import m01.remote.interfaces


class IScrapyPackage(m01.mongo.interfaces.IMongoStorageItem):
    """ScrapySpider"""

    serverName = zope.schema.TextLine(
        title=u'Server Name',
        description=u'Server Name',
        required=True)

    pkgName = zope.schema.TextLine(
        title=u'Package Name',
        description=u'Package Name',
        required=True)

    pkgVersion = zope.schema.TextLine(
        title=u'Package Version',
        description=u'Package Version',
        required=True)

    pyVersion = zope.schema.TextLine(
        title=u'Python Version',
        description=u'Python Version',
        required=True)

    md5Digest = zope.schema.TextLine(
        title=u'MD5 checksum',
        description=u'MD5 checksum',
        required=False)

    spiderNames = m01.mongo.schema.MongoList(
        title=u'Spiders Names',
        description=u'Spiders Names',
        value_type=zope.schema.TextLine(
            title=u'Spider Name',
            description=u'Spider Name',
            required=True),
        default=[],
        required=False)


# jobs
class IJobBase(m01.remote.interfaces.IJob):
    """Base class for jobs restricted to a group of servers"""

    # the job only get processed on one of the given server names
    serverNames = m01.mongo.schema.MongoList(
        title=u'Server Names',
        description=u'Server Names',
        value_type=zope.schema.TextLine(
            title=u'Server Name',
            description=u'Server Name',
            required=True),
        default=[],
        required=True)


class IAddPackage(IJobBase):
    """Add and install a package job"""

    pkgName = zope.schema.TextLine(
        title=u'Package Name',
        description=u'Package Name',
        required=True)

    pkgVersion = zope.schema.TextLine(
        title=u'Package Version',
        description=u'Package Version',
        required=True)

    pyVersion = zope.schema.TextLine(
        title=u'Python Version',
        description=u'Python Version',
        default=u'2.6',
        required=True)

    md5Digest = zope.schema.TextLine(
        title=u'MD5 checksum',
        description=u'MD5 checksum',
        required=False)

    testing = zope.schema.Bool(
        title=u'Marker for run buildout tests',
        description=u'Marker for run buildout tests',
        required=True)


class IRunSpider(IJobBase):
    """Run spider job"""

    pkgName = zope.schema.TextLine(
        title=u'Package Name',
        description=u'Package Name',
        required=True)

    pkgVersion = zope.schema.TextLine(
        title=u'Package Version',
        description=u'Package Version',
        required=True)

    pyVersion = zope.schema.TextLine(
        title=u'Python Version',
        description=u'Python Version',
        default=u'2.6',
        required=True)

    spiderName = zope.schema.TextLine(
        title=u'Spider Name',
        description=u'Spider Name',
        required=True)

    cmdOption = zope.schema.ASCIILine(
        title=u'Additional buildout crawl cmd option',
        description=u'Additional buildout crawl cmd option',
        default=None,
        required=False)


class ISyncPackages(IJobBase):
    """Sync packages job"""

    # serverName from which we sync ScrapyPackages from
    sourceServerName = zope.schema.TextLine(
        title=u'Source Server Name',
        description=u'Source Server Name',
        required=True)

    testing = zope.schema.Bool(
        title=u'Marker for run buildout tests',
        description=u'Marker for run buildout tests',
        required=True)
