#
#    Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
from Products.CMFCore.DirectoryView import registerDirectory
from config import *
from packutils import zentinel, hasZenPack, addZenPack
from brand import addBranding

from Products.ZenModel.ZenPack import ZenPackBase


registerDirectory(SKINS_DIR, GLOBALS)

class ZenPack(ZenPackBase):
    """ Zenoss eggy thing """

    def install(self, zport):
        """
        Set the collector plugin
        """
        ZenPackBase.install(self, zport)
	addBranding(zport.dmd, self)


def initialize(context):
    """
    our generic setup/handler stuff which registers our skin(s) if
    zentinel is present - we are only forceably doing this because
    we don't have a quickinstaller/generic setup regime!
    """
    zport = zentinel(context)

    if zport and not hasZenPack(zport, __name__):
        addZenPack(zport, ZenPack(__name__), SKINS_DIR, SKINNAME, GLOBALS)



#
# unilaterally apply monkeypatches - maybe should zcml this bit ...
#
import monkeypatches
