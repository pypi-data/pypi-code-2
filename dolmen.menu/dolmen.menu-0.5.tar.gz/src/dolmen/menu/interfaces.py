# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface
from zope.location import ILocation
from zope.viewlet.interfaces import IViewletManager, IViewlet
from zope.security.zcml import Permission


class IMenuEntry(Interface):
    """A menu entry.
    """
    __name__ = schema.ASCIILine(
        title=u"Identifier",
        required=True)

    permission = Permission(
        title=u"Permission",
        description=u"Permission required to use this component.",
        required=True)

    title = schema.TextLine(
        required=True,
        title=u"The destination of the entry")

    selected = schema.Bool(
        required=True,
        title=u"The entry is currently selected")

    description = schema.Text(
        default=u"",
        title=u"Full description")

    url = schema.URI(
        required=True,
        title=u"The destination of the entry")


class IMenu(IViewletManager):
    """A menu component.
    """
    menu_context = schema.Object(
        schema=ILocation,
        default=None,
        required=False,
        title=u"Menu context object")
    
    context_url = schema.URI(
        required=True,
        title=u"Absolute url of the menu context")

    entries = schema.Iterable(
        default=[],
        title=u"The menu entries")

    menu_class = schema.TextLine(
        default=u"menu",
        title=u"Menu CSS class")

    entry_class = schema.TextLine(
        default=u"entry",
        title=u"Menu entries CSS class")


class IMenuEntryViewlet(IViewlet, IMenuEntry):
    """A viewlet that acts like a menu entry.
    """
    manager = schema.Object(
        schema=IMenu,
        title=u"Menu of this entry")
