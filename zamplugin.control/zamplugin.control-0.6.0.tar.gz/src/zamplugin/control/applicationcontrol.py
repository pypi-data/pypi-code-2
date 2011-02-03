##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Application Control

$Id:$"""
__docformat__ = 'restructuredtext'

import time
import zope.interface
import zope.component
from zope.location import Location
from zope.traversing.interfaces import IContainmentRoot
from zope.app.applicationcontrol.interfaces import IApplicationControl

START_TIME = time.time()


class ApplicationControl(Location):

    zope.interface.implements(IApplicationControl)
    zope.component.adapts(IContainmentRoot)

    __name__ = '++etc++ApplicationController'

    def __init__(self, context):
        self.__parent__ = context
        self.context = context

    def getStartTime(self):
        return START_TIME
