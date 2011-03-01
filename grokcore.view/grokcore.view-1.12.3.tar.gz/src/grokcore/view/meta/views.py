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
"""Grokkers for the views code."""

from zope import interface, component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserPage

import martian
from martian.error import GrokError
from martian import util

import grokcore.security
import grokcore.view
from grokcore.security.util import protect_getattr
from grokcore.view import components

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

def default_fallback_to_name(factory, module, name, **data):
    return name


class ViewGrokker(martian.ClassGrokker):
    martian.component(components.View)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.provides, default=interface.Interface)
    martian.directive(grokcore.component.name, get_default=default_view_name)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, provides, name, **kw):
        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory)
                )

        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if grokcore.security.require.bind().get(method) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, provides, name),
            callable=component.provideAdapter,
            args=(factory, adapts, provides, name),
            )
        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            return not has_render(factory)

        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)


class ViewSecurityGrokker(martian.ClassGrokker):
    martian.component(components.View)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', factory, method_name),
                callable=protect_getattr,
                args=(factory, method_name, permission),
                )
        return True



