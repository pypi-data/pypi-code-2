# -*- coding: utf-8 -*-

import martian
import zope.component
import grokcore.view
import grokcore.component

from megrok.pagetemplate.components import PageTemplate
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class PageTemplateGrokker(martian.ClassGrokker):
    martian.priority(990)
    martian.component(PageTemplate)
    martian.directive(grokcore.component.name)
    martian.directive(grokcore.view.view)
    martian.directive(grokcore.component.provides, default=IPageTemplate)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)

    def grok(self, name, factory, module_info, **kw):
        factory.module_info = module_info
        return martian.ClassGrokker.grok(
            self, name, factory, module_info, **kw)

    def execute(self, factory, config, name, view, layer, provides, **kw):
        pagetemplate = factory()
        templates = factory.module_info.getAnnotation('grok.templates', None)

        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory))

        adapts = (view, layer)
        config.action(
            discriminator=('adapter', adapts, provides, name),
            callable=zope.component.provideAdapter,
            args=(pagetemplate, adapts, provides, name))

        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            return False

        def has_no_render(factory):
            return True

        templates.checkTemplates(module_info, factory, 'pagetemplate',
                                 has_render, has_no_render)
