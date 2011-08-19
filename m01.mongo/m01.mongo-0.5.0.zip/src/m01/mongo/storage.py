##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: member.py 419 2007-04-08 00:47:45Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.container import contained

from m01.mongo import base
from m01.mongo import interfaces


class MongoStorage(base.MongoStorageBase, contained.Contained):
    """Persistent mongo item storage with thread save transaction and caching
    support.
    
    This class can be used without the ZODB.

    Note: don't forget to mixin persistent in your MongoContainer class
    if you like to store such MongoContainer in ZODB.

    """

    zope.interface.implements(interfaces.IMongoStorage)


#class SharedMongoStorage(base.SharedMongoStorageBase, contained.Contained):
#    """Persistent shared mongo item storage with thread save transaction and
#    caching support.
#
#    This implementation uses a shared collection with a namespace for group
#    items.
#    
#    This class can be used without the ZODB.
#
#    Note: don't forget to mixin persistent in your MongoContainer class
#    if you like to store such MongoContainer in ZODB.
#
#    """
#
#    zope.interface.implements(interfaces.ISharedMongoStorage)
