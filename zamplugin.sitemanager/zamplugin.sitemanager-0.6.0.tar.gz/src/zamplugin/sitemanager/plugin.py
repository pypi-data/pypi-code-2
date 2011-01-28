##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.component

from z3c.baseregistry import baseregistry

from zam.api.i18n import MessageFactory as _
from zam.api import plugin


SiteManagerBaseRegistry = baseregistry.BaseComponents(
    zope.component.globalSiteManager, 'zamplugin.sitemanager')


class SiteManagerPlugin(plugin.BaseRegistryPlugin):
    """ZAM sitemanager plugin."""

    registry = SiteManagerBaseRegistry

    title = _("Site management")

    description = _("ZAM Site Manager.")
