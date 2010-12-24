# -*- coding: utf-8 -*-

import grokcore.viewlet
import martian
import sys
import types
import zope.component

from dolmen.menu.interfaces import IMenu, IMenuEntry
from martian.error import GrokImportError
from martian.util import frame_is_module
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from grokcore.view.meta.views import default_view_name


EXTRACTABLES = {
    'name': grokcore.viewlet.name.bind(get_default=default_view_name),
    'title': grokcore.viewlet.title.bind(get_default=default_view_name),
    'description': grokcore.viewlet.description.bind(default=u""),
    'context': grokcore.viewlet.context.bind(default=Interface),
    'layer': grokcore.viewlet.layer.bind(default=IDefaultBrowserLayer),
    'view': grokcore.viewlet.view.bind(default=Interface),
    'permission': grokcore.viewlet.require.bind(default='zope.View'),
    'order': grokcore.viewlet.order.bind(),
    }


def get_entry_values(factory, **extras):
    values = {}
    for name, directive in EXTRACTABLES.items():
        if name in extras:
            values[name] = extras.get(name)
        else:
            value = directive.get(factory)
            values[name] = value
    return values


def validateMenu(directive, value):
    if not IMenu.implementedBy(value):
        raise ValueError(
            "You can only register a menu item on a IMenu component.")


class menu(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = validateMenu


class global_menuentry(martian.MultipleTimesDirective):
    scope = martian.MODULE

    def factory(self, component, menu, **args):
        validateMenu(self, menu)
        if not martian.util.isclass(component):
            raise TypeError(
                "`global_menuentry` can only be used with class components."
                " For functions, use directly zope.component.provideAdapter")
        return (component, menu, args)


class menuentry:
    """Annotates the class for further grokking
    """

    def __init__(self, menu, **args):
        self.menu = menu
        self.infos = args

    def __call__(self, entry):
        frame = sys._getframe(1)
        if not frame_is_module(frame):
            raise GrokImportError(
                "@dolmen.menu.menuentry can only be used at the module level")

        if not self.menu:
            raise GrokImportError(
                "@dolmen.menu.menuentry requires at least one argument.")

        values = get_entry_values(entry, **self.infos)
        context = values.get('context')
        view = values.get('view')
        layer = values.get('layer')
        menu = self.menu

        if type(entry) is types.FunctionType:
            adapter = zope.component.adapter(context, layer, view, menu)
            implementer = zope.interface.implementer(IMenuEntry)

            adapter(entry)
            implementer(entry)

            adapters = frame.f_locals.get('__grok_adapters__', None)
            if adapters is None:
                frame.f_locals['__grok_adapters__'] = adapters = []
            adapters.append(entry)

        else:
            entries = frame.f_locals.get('__grok_menuentries__', None)
            if entries is None:
                frame.f_locals['__grok_menuentries__'] = entries = []
            entries.append((entry, self.menu, self.infos))

        return entry
