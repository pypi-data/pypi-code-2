##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Evolve existing PAU group folders.

They should be used as contained plugins rather than registered plugins.
"""
__docformat__ = "reStructuredText"

import zope.app.authentication.interfaces
from zope.app.authentication import groupfolder
from zope.app.component.interfaces import ISite
from zope.component import getUtilitiesFor
from zope.copypastemove.interfaces import IObjectMover
from zope.generations.utility import findObjectsProviding, getRootFolder

generation = 3

def evolve(context):
    """Evolve existing PAUs and group folders.

    - Group folders should no longer be registered.

    - PAUs that use group folders should use their contents name, not their
      (formerly) registered name.

    Group folders used by multiple PAUs were not supported, and are not
    supported with this evolution.
    """
    root = getRootFolder(context)

    for site in findObjectsProviding(root, ISite):
        sm = site.getSiteManager()
        for pau in findObjectsProviding(
            sm, zope.app.authentication.interfaces.IPluggableAuthentication):
            for nm, util in getUtilitiesFor(
                zope.app.authentication.interfaces.IAuthenticatorPlugin,
                context=pau):
                if groupfolder.IGroupFolder.providedBy(util):
                    if util.__parent__ is not pau:
                        raise RuntimeError(
                            "I don't know how to migrate your database: "
                            "each group folder should only be within the "
                            "Pluggable Authentication utility that uses it")
                    # we need to remove this registration
                    regs = [r for r in sm.registeredUtilities()
                            if r.component == util]
                    if len(regs) != 1:
                        raise RuntimeError(
                            "I don't know how to migrate your database: "
                            "you should only have registered your group "
                            "folder as an IAuthenticatorPlugin, but it looks "
                            "like it's registered for something additional "
                            "that I don't expect")
                    r = regs[0]
                    sm.unregisterUtility(
                       util,
                       zope.app.authentication.interfaces.IAuthenticatorPlugin,
                       nm)
                    if r.name in pau.authenticatorPlugins:
                        if util.__name__ != r.name: # else no-op
                            plugins = list(pau.authenticatorPlugins)
                            if util.__name__ in pau.authenticatorPlugins:
                                # argh! another active plugin's name is
                                # the same as this group folder's
                                # __name__.  That means we need to choose
                                # a new name that is also not in
                                # authenticatorPlugins and not in
                                # pau.keys()...
                                ct = 0
                                nm = '%s_%d' % (util.__name__, ct)
                                while (nm in pau.authenticatorPlugins or
                                       nm in pau):
                                    ct += 1
                                    nm = '%s_%d' % (util.__name__, ct)
                                IObjectMover(util).moveTo(pau, nm)
                            plugins[plugins.index(r.name)] = util.__name__
                            pau.authenticatorPlugins = tuple(plugins)
            for k, r in pau.registrationManager.items():
                if groupfolder.IGroupFolder.providedBy(r.component):
                    del pau.registrationManager[k]

