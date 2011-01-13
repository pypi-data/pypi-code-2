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

import zope.interface
import zope.component
import zope.schema
from zope.contentprovider.interfaces import IContentProvider

from zam.api.i18n import MessageFactory as _


class IPlugin(zope.interface.Interface):
    """A component that provides additional features to a site."""

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title.'),
        required=True)

    description = zope.schema.Text(
        title=_(u'Description'),
        description=_(u'The depscription.'),
        required=True)

    def isInstalled(site):
        """Checks whether the plugin is installed for the site."""

    def install(site):
        """Install the plugin for the site.

        If the plugin is already installed, do nothing.
        """

    def uninstall(site):
        """Uninstall the plugin from the site.

        If the plugin is already uninstalled, do nothing.
        """


class IBaseRegistryPlugin(IPlugin):

    registry = zope.schema.Object(
        title=_(u'Registry'),
        description=_(u'The base registry to be inserted into the site.'),
        schema=zope.component.interfaces.IComponents,
        required=True)


class IPluginManagement(IContentProvider):
    """Plugin management content provider."""


# selected menu marker for pages
class IRootMenuItemPage(zope.interface.Interface):
    """Containment root page marker."""
