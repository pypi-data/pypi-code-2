# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute, moduleProvides


class IComponent(Interface):
    """A named component.
    """
    identifier = Attribute(u"Component id")
    title = Attribute(u"Component title")

    def clone(new_identifier=None):
        """Return a clone of the new component, with identifier
        new_identifier if it is not None.
        """


class IComponentFactory(Interface):
    """Component used to built components.
    """

    def produce(self):
        """Should generate components.
        """


class ICollection(Interface):
    """Support to manage a collection of ordered named components.
    """
    type = Attribute(
        u"Interface restricting the type of component")
    factory = Attribute(
        u"Interface to query in order to get a factory to extend "
        u"collection with unknow components.")

    def append(component):
        """Add a new component to the collection. Modify the current
        collection.
        """

    def extend(*component):
        """Create/Add a list of components to the collection. Modify
        the current collection.
        """

    def get(id, default=None):
        """Return the component with the given ID.
        """

    def select(*ids):
        """Return a copy containing only the given named components.
        """

    def omit(*ids):
        """Return a copy containing all but none of the given named
        components.
        """

    def copy():
        """Return a copy of the collection.
        """

    def clear():
        """Empty the collection: remove all components from it.
        """

    def keys():
        """Return all components id contained in the collection.
        """

    def __add__(other):
        """Create a collection as copy of self, and add value for
        other component or collection.
        """

    def __getitem__(id):
        """Return the given component identified by id or raise
        KeyError.
        """

    def __contains__(id):
        """Return true if the collection contains a component
        identified by id.
        """

    def __iter__():
        """Return an iterator on the components.
        """

    def __len__():
        """Return the numbre of components.
        """


class IMutableCollection(ICollection):
    """A collection that can be changed.
    """

    def set(id, value):
        """Change component associated to this id.
        """

    def __setitem__(id, value):
        """Change component associated to this id.
        """

    def __delitem__(id):
        """Remove the component associated to this id.
        """


class ICollectionAPI(Interface):
    IComponent = Attribute(
        "A named component.")
    IComponentFactory = Attribute(
        "Component used to built components.")
    ICollection = Attribute(
        "Support to manage a collection of ordered named components.")
    IMutableCollection = Attribute(
        "A collection that can be changed.")


moduleProvides(ICollectionAPI)
__all__ = list(ICollectionAPI)
