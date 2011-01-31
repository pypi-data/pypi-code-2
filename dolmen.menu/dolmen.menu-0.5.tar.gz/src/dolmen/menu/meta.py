# -*- coding: utf-8 -*-

import martian
import dolmen.menu
import grokcore.view

from grokcore.view.meta.views import default_view_name
from zope import component, interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


def generate_entry(bdict):
    id = bdict['__view_name__'] = bdict['__name__'] = bdict['name']
    return id, type(id, (dolmen.menu.Entry,), bdict)


def register_entry(factory, menu, infos, config=None):
    # We get the values from the directives
    values = dolmen.menu.get_entry_values(factory, **infos)

    # We pop the values issued from directives.
    context = values.pop('context')
    view = values.pop('view')
    layer = values.pop('layer')
    order = values.pop('order')

    # We generate the entry.
    entry_name, entry = generate_entry(values)

    # If order was not from a directive, we set it back, for later sorting.
    if not isinstance(order, tuple):
        grokcore.view.order.set(entry, (order, 1))

    # We enqueue our component in the registry config.
    config.action(
        discriminator=('menuentry', context, layer, view, menu, entry_name),
        callable=component.provideAdapter,
        args=(entry, (context, layer, view, menu),
              dolmen.menu.IMenuEntry, entry_name))


class PreAdapterDecoratorGrokker(martian.GlobalGrokker):
    martian.priority(1000)
    
    def grok(self, name, module, module_info, config, **kw):
        callbacks = module_info.getAnnotation('dolmen.menufunctions', [])
        for register in callbacks:
            register()
        return True


class MenuEntryGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        callbacks = module_info.getAnnotation('dolmen.menuclasses', [])
        for register in callbacks:
            register(register_entry, config)
        return True


class ViewletMenuEntriesGrokker(martian.ClassGrokker):
    martian.component(dolmen.menu.Entry)
    martian.directive(grokcore.view.context)
    martian.directive(grokcore.view.view, default=interface.Interface)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.view.name, get_default=default_view_name)
    martian.directive(dolmen.menu.menu, default=None)

    def execute(self, factory, config, context, menu, view, layer, name, **kw):

        if not context:
            raise ValueError("No Context")

        if not menu:
            raise ValueError("No menu")

        if interface.interfaces.IInterface.providedBy(menu):
            if not menu.isOrExtends(dolmen.menu.IMenu):
                raise ValueError("Invalid menu type")
        else:
            if not dolmen.menu.IMenu.implementedBy(menu):
                raise ValueError("Invalid menu type")

        factory.__name__ = factory.__view_name__ = name
        interface.verify.verifyClass(dolmen.menu.IMenuEntry, factory)

        # We enqueue our component in the registry config.
        config.action(
            discriminator=('menu-entry', context, layer,
                           view, menu, name),
            callable=component.provideAdapter,
            args=(factory, (context, layer, view, menu),
                  dolmen.menu.IMenuEntry, name))

        return True
