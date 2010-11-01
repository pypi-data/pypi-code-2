#############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Grokkers for the various components."""

from zope import component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager, IViewlet

import martian
from martian.util import scan_for_classes
from martian.error import GrokError

import grokcore.component
from grokcore.component.interfaces import IContext
from grokcore.component.meta import default_context
import grokcore.view
import grokcore.security

import grokcore.viewlet
from grokcore.viewlet import components
from grokcore.viewlet.util import make_checker
from grokcore.viewlet.interfaces import IViewletManager as IGrokViewletManager

from grokcore.view.meta.views import default_view_name


class ViewletManagerGrokker(martian.ClassGrokker):
    martian.component(grokcore.viewlet.ViewletManager)
    martian.directive(grokcore.component.context, get_default=default_context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.view)
    martian.directive(grokcore.component.name, get_default=default_view_name)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewletManagerGrokker, self).grok(
            name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, view, name, **kw):
        # This will be used to support __name__ on the viewlet manager
        factory.__view_name__ = name

        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory))

        config.action(
            discriminator=('viewletManager', context, layer, view, name),
            callable=component.provideAdapter,
            args=(factory, (context, layer, view), IViewletManager, name))
        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            return factory.render != components.ViewletManager.render

        def has_no_render(factory):
            # always has a render method
            return False

        templates.checkTemplates(module_info, factory, 'viewlet manager',
                                 has_render, has_no_render)

def default_viewletmanager(factory, module, **data):
    components = list(scan_for_classes(module, IGrokViewletManager))
    if len(components) == 0:
        raise GrokError(
            "No module-level viewletmanager for %r, please use the "
            "'viewletmanager' directive." % (factory), factory)
    elif len(components) == 1:
        component = components[0]
    else:
        raise GrokError(
            "Multiple possible viewletmanagers for %r, please use the "
            "'viewletmanager' directive."
            % (factory), factory)
    return component

class ViewletGrokker(martian.ClassGrokker):
    martian.component(grokcore.viewlet.Viewlet)
    martian.directive(grokcore.component.context, get_default=default_context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.view)
    martian.directive(
        grokcore.viewlet.viewletmanager, get_default=default_viewletmanager)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.security.require, name='permission')

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewletGrokker, self).grok(
            name, factory, module_info, **kw)

    def execute(self, factory, config,
                context, layer, view, viewletmanager, name, permission, **kw):
        # This will be used to support __name__ on the viewlet
        factory.__view_name__ = name

        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory))

        config.action(
            discriminator=(
                'viewlet', context, layer, view, viewletmanager, name),
            callable=component.provideAdapter,
            args=(factory, (context, layer, view, viewletmanager),
                  IViewlet, name))

        config.action(
            discriminator=('protectName', factory, '__call__'),
            callable=make_checker,
            args=(factory, factory, permission, ['update', 'render']))

        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            return factory.render != components.Viewlet.render

        def has_no_render(factory):
            return not has_render(factory)

        templates.checkTemplates(module_info, factory, 'viewlet',
                                 has_render, has_no_render)
