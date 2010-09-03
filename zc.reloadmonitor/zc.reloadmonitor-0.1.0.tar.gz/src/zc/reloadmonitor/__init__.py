##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

import sys
import zope.component
import zope.interface
import zc.monitor.interfaces

@zope.interface.provider(zc.monitor.interfaces.IMonitorPlugin)
def reloadmonitor(connection, name):
    """reload an already-imported module

    Usage: reload module.name

    Note that the usual Python reload semantics apply.  For example,
    long-lived instances of classes defined in the module are unaffected.
    """
    reload(sys.modules[name])
    print >>connection, 'done'

def configure(name='reload'):
    zope.component.provideUtility(reloadmonitor, name=name)
