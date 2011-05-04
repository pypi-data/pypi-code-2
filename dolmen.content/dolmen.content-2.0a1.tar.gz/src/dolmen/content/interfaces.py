# -*- coding: utf-8 -*-

import zope.component.interfaces
from dolmen.field import GlobalClass
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
from zope.schema import TextLine

# Convenient imports.
from dolmen.container.interfaces import IContainer, IOrderedContainer

_ = MessageFactory('zope')


class IContent(Interface):
    """Marker interface for contentish dolmen objects.
    """
    __content_type__ = Attribute(
        """Type of the object. Usually set by the grokker, using the
        grok.name directive.""")


class IFactory(zope.component.interfaces.IFactory):
    """A factory for a dolmen content type.
    """
    factory = GlobalClass(
        required=True,
        title=u"Class used as a factory",
        schema=IContent)

    addform = TextLine(
        required=True,
        title=u"Name of the add form",
        default=u"add")

    name = TextLine(
        required=True,
        title=u"Name of the factored content",
        default=u"")

    title = TextLine(
        required=False,
        title=u"Title of the factored content",
        default=u"")

    description = TextLine(
        required=False,
        title=u"Description of the factored content",
        default=u"")

    def getSchema():
        """Returns a list of interfaces representing the schema
        of the factored item. The returned interfaces must be provided
        by the instance of the object issued from the factory.
        """


__all__ = ('IContent', 'IContainer', 'IOrderedContainer', 'IFactory')
