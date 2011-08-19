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

from m01.mongo import interfaces
from m01.mongo import base


class MongoContainer(base.MongoContainerBase, contained.Contained):
    """Mongo storage based container supporting item with __name__.
    
    This class can be used without the ZODB.

    Note: don't forget to mixin persistent in your MongoContainer class
    if you like to store such MongoContainer in ZODB.
    """

    zope.interface.implements(interfaces.IMongoContainer)


#class SharedMongoContainer(base.SharedMongoContainerBase, contained.Contained):
#    """Mongo container with shared collection using a namespace for group items.
#    
#    This class can be used without the ZODB.
#
#    Note: don't forget to mixin persistent in your MongoContainer class
#    if you like to store such MongoContainer in ZODB.
#    """
#
#    zope.interface.implements(interfaces.ISharedMongoContainer)
