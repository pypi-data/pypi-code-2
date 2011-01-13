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
import zope.interface
from zope.app.renderer import rest
from z3c.pagelet import browser
from z3c.form import button
from z3c.formui import form

from z3c.template.template import getPageTemplate

from zam.api import interfaces
from zam.api.i18n import MessageFactory as _


def render(text, request):
    return rest.ReStructuredTextToHTMLRenderer(text, request).render()


def showInstall(form):
    if form.isInstalled:
        return False
    return True

def showUnInstall(form):
    if form.isInstalled:
        return True
    return False
    

class PluginManagement(form.Form):
    """Single plugin management form."""

    zope.interface.implements(interfaces.IPluginManagement)

    template = getPageTemplate('subform')
    _prefix = 'will_be_set_by_parent'

    installedCSS = 'installedPlugin'
    notInstalledCSS = 'notInstalledPlugin'

    installMessage = _('Plugin status successfully installed.')
    uninstallMessage = _('Plugin status successfully un-installed.')

    def __init__(self, context, request, site):
        super(PluginManagement, self).__init__(context, request)
        self.site = site

    @apply
    def prefix():
        # parent page will set the prefix for each plugin form
        def get(self):
            return self._prefix
        def set(self, prefix):
            # base registry (utility) names are unicode
            prefix = prefix.encode('utf-8')
            self._prefix = prefix
        return property(get, set)

    @property
    def title(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    @property
    def isInstalled(self):
        return self.context.isInstalled(self.site)

    @property
    def statusCSS(self):
        return self.isInstalled and self.installedCSS or self.notInstalledCSS

    @button.buttonAndHandler(_('Install'), name='install',
        condition=showInstall)
    def handleInstall(self, action):
        self.context.install(self.site)
        self.status = self.installMessage
        self.request.response.redirect(self.request.getURL())
        return u''

    @button.buttonAndHandler(_('Uninstall'), name='uninstall',  
        condition=showUnInstall)
    def handleUnInstall(self, action):
        self.context.uninstall(self.site)
        self.status = self.uninstallMessage
        self.request.response.redirect(self.request.getURL())
        return u''


class PluginsPage(browser.BrowserPagelet):
    """Plugin management page."""

    template = getPageTemplate()

    def pluginForms(self):
        forms = []
        for name, plugin in zope.component.getUtilitiesFor(interfaces.IPlugin):
            pluginForm = zope.component.queryMultiAdapter(
                (plugin, self.request, self.context),
                interface=interfaces.IPluginManagement)
            if pluginForm is not None:
                pluginForm.prefix = name
                pluginForm.update()
                forms.append(pluginForm)
        return forms
