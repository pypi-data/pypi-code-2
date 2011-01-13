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

from zope.viewlet.interfaces import IViewletManager
from zope.publisher.interfaces.browser import IBrowserRequest

import z3c.layer.ready2go


# this plugin layers allows us to use the zam plugin configuration without
# to make the skin depend on the plugins.
class IContentsPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.contents package."""

class IAuthenticatorPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.authentication package."""

class IControlPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.control package."""

class IErrorPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.error package."""

class INavigationPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.navigation package."""

class ISampleDataPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.sampledata package."""

class ISiteManagerPluginLayer(IBrowserRequest):
    """Plugin layer offered for zamplugin.sitemanager package."""


# ZAM core Layer
class IZAMCoreLayer(z3c.layer.ready2go.IReady2GoBrowserLayer):
    """ZAM browser layer without any plugin configuration."""


class IZAMPluginLayer(IContentsPluginLayer, IAuthenticatorPluginLayer,
    IControlPluginLayer, IErrorPluginLayer, INavigationPluginLayer,
    ISampleDataPluginLayer, ISiteManagerPluginLayer):
    """Plugin layer offered for zamplugin configuration."""


class IZAMBrowserLayer(IZAMPluginLayer, IZAMCoreLayer):
    """ZAM browser layer including ``all in one`` configuration."""


# ZAM viewlet manager
class ICSS(IViewletManager):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


class IBreadcrumb(IViewletManager):
    """Breadcrumb viewlet manager."""


class ISideBar(IViewletManager):
    """SideBar viewlet manager."""
