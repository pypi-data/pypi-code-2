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
"""Grokkers for templates."""

import martian

from grokcore.view import components
from grokcore.view import templatereg


class TemplateGrokker(martian.GlobalGrokker):
    # this needs to happen before any other grokkers execute that use
    # the template registry
    martian.priority(1001)

    def grok(self, name, module, module_info, config, **kw):
        module.__grok_templates__ = templatereg.TemplateRegistry()
        return True


class ModulePageTemplateGrokker(martian.InstanceGrokker):
    martian.component(components.BaseTemplate)
    # this needs to happen before any other grokkers execute that actually
    # use the templates
    martian.priority(1000)

    def grok(self, name, instance, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.register,
            args=(name, instance)
            )
        config.action(
            discriminator=None,
            callable=instance._annotateGrokInfo,
            args=(name, module_info.dotted_name)
            )
        return True


class FilesystemPageTemplateGrokker(martian.GlobalGrokker):
    # do this early on, but after ModulePageTemplateGrokker, as
    # findFilesystem depends on module-level templates to be
    # already grokked for error reporting
    martian.priority(999)

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.findFilesystem,
            args=(module_info,)
            )
        return True


class UnassociatedTemplatesGrokker(martian.GlobalGrokker):
    martian.priority(-1001)

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False

        config.action(
            discriminator=None,
            callable=templates.checkUnassociated,
            args=(module_info,)
            )
        return True

