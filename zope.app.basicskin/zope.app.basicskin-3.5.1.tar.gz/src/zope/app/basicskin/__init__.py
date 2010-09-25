##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Basic skin

$Id: __init__.py 106669 2009-12-16 22:42:40Z hannosch $
"""
__docformat__ = 'restructuredtext'
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class IBasicSkin(IDefaultBrowserLayer):
    """Basic skin that simply only contains the default layer and
    nothing else"""
