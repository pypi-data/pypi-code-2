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
"""mongodb connection

$Id:$
"""
__docformat__ = "reStructuredText"

import time

from m01.mongo import pool

from s01.core import util


def mongoConnectionPoolFactory(confKey, envKey):
    parts = util.getConfig('s01.core', confKey, envKey)
    if not parts:
        raise ValueError(
            "Missing mongodb in buildout.cfg, define 'host:port' or 'testing'")
    if parts == 'testing':
        import m01.mongo.testing
        return m01.mongo.testing.FakeMongoConnectionPool()
    elif ':' not in parts:
        raise ValueError(
            "mongodb in buildout.cfg must define 'host:port' or 'testing'")
    host, port = parts.split(':')
    return pool.MongoConnectionPool(str(host), int(port))

mongoConnectionPool = mongoConnectionPoolFactory('mongodb', 'S01_CORE_MONGODB')


# mongo collection getter
def getRemoteFactories():
    """JobFactory storage collection"""
    connection = mongoConnectionPool.connection
    return connection.s01.factories


def getRemoteJobs():
    """Job storage collection"""
    connection = mongoConnectionPool.connection
    return connection.s01.jobs


def getScrapyPackages():
    """ScrapyPackage storage collection"""
    connection = mongoConnectionPool.connection
    return connection.s01.packages


def setUpMongoDB(sleep=0):
    """Setup MongoDB indexes"""
    # setup MongoDB indexes

    # m01.remote.interfaces.IJob (jobs as factories)
    # s01.factories
    collection = getRemoteFactories()
    collection.ensure_index('__name__', unique=True)

    # m01.remote.interfaces.IJob (processing jobs)
    # s01.jobs
    collection = getRemoteJobs()
    collection.ensure_index('__name__', unique=True)
    collection.ensure_index('active')
    collection.ensure_index('status')
    collection.ensure_index([('queued', 1)])

    # s01.core.interfaces.IScrapyPackage
    # s01.packages
    collection = getScrapyPackages()
    collection.ensure_index('__name__', unique=True)
    collection.ensure_index('serverName')
    collection.ensure_index('pkgName')
    collection.ensure_index('pkgVersion')
    collection.ensure_index('pyVersion')

    if sleep:
        # usable for testing
        time.sleep(sleep)
