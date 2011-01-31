# -*- coding: utf-8 -*-

import martian
import sys
import types
import zope.interface
import zope.component

from grokcore import view
from martian.error import GrokImportError
from martian.util import frame_is_module
from dolmen.menu.interfaces import IMenu, IMenuEntry
from grokcore.view.meta.views import default_view_name
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface


EXTRACTABLES = {
    'name': view.name.bind(get_default=default_view_name),
    'title': view.title.bind(get_default=default_view_name),
    'description': view.description.bind(default=u""),
    'context': view.context.bind(default=Interface),
    'layer': view.layer.bind(default=IDefaultBrowserLayer),
    'view': view.view.bind(default=Interface),
    'permission': view.require.bind(default='zope.View'),
    'order': view.order.bind(),
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


def function_menu_entry(frame, entry, menu, infos):
    def register():
        values = get_entry_values(entry, **infos)
        context = values.get('context')
        view = values.get('view')
        layer = values.get('layer')
        adapter = zope.component.adapter(context, layer, view, menu)
        implementer = zope.interface.implementer(IMenuEntry)
        adapter(entry)
        implementer(entry)
        adapters = frame.f_locals.get('__grok_adapters__', None)
        if adapters is None:
            frame.f_locals['__grok_adapters__'] = adapters = []
        adapters.append(entry)
    return register


def class_menu_entry(frame, entry, menu, infos):
    def register(register_method, config):
        register_method(entry, menu, infos, config)
    return register


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

        frame = sys._getframe(2)
        entries = frame.f_locals.get('__dolmen_menuclasses__', None)
        if entries is None:
            frame.f_locals['__dolmen_menuclasses__'] = entries = []
            callback = class_menu_entry
        entries.append(callback(frame, component, menu, args))
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

        if type(entry) is types.FunctionType:
            entries = frame.f_locals.get('__dolmen_menufunctions__', None)
            if entries is None:
                frame.f_locals['__dolmen_menufunctions__'] = entries = []
            callback = function_menu_entry
        else:
            entries = frame.f_locals.get('__dolmen_menuclasses__', None)
            if entries is None:
                frame.f_locals['__dolmen_menuclasses__'] = entries = []
            callback = class_menu_entry
        entries.append(callback(frame, entry, self.menu, self.infos))
        return entry
