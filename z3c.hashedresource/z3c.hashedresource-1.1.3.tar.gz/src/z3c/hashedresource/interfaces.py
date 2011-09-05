#############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

$Id$
"""
from zope.interface import Interface, alsoProvides
import zope.publisher.interfaces.browser


class IResourceContentsHash(Interface):

    def __str__():
        """return a hash of the contents of the resource"""


class IHashedResourceSkin(
    zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """marker interface to differentiate our AbsoluteURL registration
    from the default one in zope.app.publisher."""

alsoProvides(
    IHashedResourceSkin, zope.publisher.interfaces.browser.IBrowserSkinType)
