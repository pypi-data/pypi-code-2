###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.interface

import m01.remote.job
from m01.mongo.fieldproperty import MongoFieldProperty

from s01.core import interfaces


class JobBase(m01.remote.job.Job):
    """Job with dict as input data"""

    def applyInputData(self, data, input=None):
        # update existing data with the given input data
        if input is not None:
            data.update(input)


class RunSpider(JobBase):
    """Run a buildout based scrapy spider"""

    zope.interface.implements(interfaces.IRunSpider)

    serverNames = MongoFieldProperty(interfaces.IRunSpider['serverNames'])
    pkgName = MongoFieldProperty(interfaces.IRunSpider['pkgName'])
    pkgVersion = MongoFieldProperty(interfaces.IRunSpider['pkgVersion'])
    pyVersion = MongoFieldProperty(interfaces.IRunSpider['pyVersion'])
    spiderName = MongoFieldProperty(interfaces.IRunSpider['spiderName'])
    cmdOption = MongoFieldProperty(interfaces.IRunSpider['cmdOption'])

    dumpNames = ['serverNames', 'pkgName', 'pkgVersion', 'pyVersion',
                 'spiderName', 'cmdOption',
                ]

    def __call__(self, remoteProcessor):
        """Run a buildout based scrapy spider in a subprocess"""
        raiseError = True
        return remoteProcessor.runSpider(self.pkgName, self.pkgVersion,
            self.pyVersion, self.spiderName, self.cmdOption, raiseError)


class AddPackage(JobBase):
    """Knows how to add and install a package"""

    zope.interface.implements(interfaces.IAddPackage)

    serverNames = MongoFieldProperty(interfaces.IAddPackage['serverNames'])
    pkgName = MongoFieldProperty(interfaces.IAddPackage['pkgName'])
    pkgVersion = MongoFieldProperty(interfaces.IAddPackage['pkgVersion'])
    pyVersion = MongoFieldProperty(interfaces.IAddPackage['pyVersion'])
    testing = MongoFieldProperty(interfaces.IAddPackage['testing'])
    md5Digest = MongoFieldProperty(interfaces.IAddPackage['md5Digest'])

    dumpNames = ['serverNames', 'pkgName', 'pkgVersion', 'pyVersion',
                 'testing', 'md5Digest',
                ]

    def __call__(self, remoteProcessor):
        """Run a buildout based scrapy spider in a subprocess"""
        raiseError = True
        return remoteProcessor.addPackage(self.pkgName, self.pkgVersion,
            self.pyVersion, self.md5Digest, self.testing, raiseError)


class SyncPackages(JobBase):
    """Knows how to add installation jobs for all missing packages"""

    zope.interface.implements(interfaces.ISyncPackages)

    serverNames = MongoFieldProperty(interfaces.ISyncPackages['serverNames'])
    sourceServerName = MongoFieldProperty(
        interfaces.ISyncPackages['sourceServerName'])
    testing = MongoFieldProperty(interfaces.ISyncPackages['testing'])

    dumpNames = ['serverNames', 'sourceServerName', 'testing']

    def __call__(self, remoteProcessor):
        """Run a buildout based scrapy spider in a subprocess"""
        data = remoteProcessor.getMissingPackageVersions(self.sourceServerName)
        out = []
        for d in data:
            pkgName = d['pkgName']
            pkgVersion = d['pkgVersion']
            pyVersion = d.get('pyVersion', None)
            # our server knows how to add a job which can add a package for our
            # server by using our serverName as job filter
            out.append(remoteProcessor.startAddPackage(pkgName, pkgVersion,
                pyVersion, testing=self.testing))
        return out
