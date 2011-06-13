# -*- coding: utf-8 -*-

import re
from zope import component
from zope.interface import implements
from dolmen.collection.load import loadComponents
from dolmen.collection.interfaces import (
    IComponent, ICollection, IMutableCollection)

_marker = object()
_valid_identifier = re.compile('[A-Za-z][A-Za-z0-9_-]*$')


class Marker(object):
    pass


class OVERRIDE(Marker):
    pass


class UNIQUE(Marker):
    pass


class IGNORE(Marker):
    pass


def createId(name):
    # Create a valid id from any string.
    identifier = unicode(name).strip().encode('utf-8').replace(' ', '-')
    if _valid_identifier.match(identifier):
        return identifier.lower()
    return identifier.encode('hex')


class Component(object):
    implements(IComponent)

    identifier = None
    title = None

    def __init__(self, title=None, identifier=None):
        if not self.title:
            if not title:
                # If the title is empty, use the identifier as title
                title = identifier
                if title is None:
                    raise ValueError(
                        u"Need at least a title to build a component.")
            self.title = title
        if identifier is None:
            identifier = createId(self.title)
        self.identifier = str(identifier)

    def clone(self, new_identifier=None):
        return self.__class__(self.title, new_identifier)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.title)


class Collection(object):
    """Represent a collection of components.
    """
    implements(ICollection)

    type = IComponent
    factory = None
    behavior = UNIQUE

    def __init__(self, *components, **options):
        self.__options = {}
        for name, value in options.items():
            if name not in ICollection:
                self.__options[name] = value
        self.__dict__.update(self.__options)
        self.__ids = []
        self.__components = []
        if len(components):
            self.extend(*components)

    def reverse(self):
        self.__components = [c for c in reversed(self.__components)]
        self.__ids = [c.identifier for c in self.__components]

    def sort(self, cmp=cmp, key=lambda c: c.identifier, reverse=False):
        self.__components.sort(cmp=cmp, key=key, reverse=reverse)
        self.__ids = [c.identifier for c in self.__components]

    def clear(self):
        self.__ids = []
        self.__components = []

    def get(self, id, default=_marker):
        try:
            return self.__components[self.__ids.index(id)]
        except ValueError:
            if default is _marker:
                raise KeyError(id)
            return default

    def set(self, id, value):
        if not IMutableCollection.providedBy(self):
            raise NotImplementedError
        if not self.type.providedBy(value):
            raise TypeError(value)
        try:
            self.__components[self.__ids.index(id)] = value
        except ValueError:
            raise KeyError(id)

    def append(self, component):
        if self.type.providedBy(component):
            if component.identifier in self.__ids:
                if issubclass(self.behavior, OVERRIDE):
                    self.set(component.identifier, component)
                elif issubclass(self.behavior, UNIQUE):
                    raise ValueError(
                        u"Duplicate identifier", component.identifier)
            else:
                self.__ids.append(component.identifier)
                self.__components.append(component)
        else:
            raise TypeError(u"Invalid type", component)

    def extend(self, *components):
        for cmp in components:
            if self.type.providedBy(cmp):
                self.append(cmp)
            elif ICollection.providedBy(cmp):
                for item in cmp:
                    self.append(item)
            else:
                if self.factory is not None:
                    loadComponents()
                    factory = component.queryAdapter(cmp, self.factory)
                    if factory is not None:
                        for item in factory.produce():
                            self.append(item)
                        continue
                raise TypeError(u'Invalid type', cmp)

    def select(self, *ids):
        components = (c for c in self.__components if c.identifier in ids)
        return self.__class__(*components, **self.__options)

    def omit(self, *ids):
        components = (c for c in self.__components if c.identifier not in ids)
        return self.__class__(*components, **self.__options)

    def copy(self):
        return self.__class__(*self.__components, **self.__options)

    def keys(self):
        return list(self.__ids)

    def __add__(self, other):
        if ICollection.providedBy(other):
            copy = self.copy()
            for component in other:
                copy.append(component)
            return copy
        if IComponent.providedBy(other):
            copy = self.copy()
            copy.append(other)
            return copy
        raise NotImplementedError

    def __getitem__(self, id):
        return self.get(id)

    def __setitem__(self, id, value):
        self.set(id, value)

    def __delitem__(self, id):
        if not IMutableCollection.providedBy(self):
            raise NotImplementedError
        try:
            index = self.__ids.index(id)
            self.__ids.remove(id)
            del self.__components[index]
        except ValueError:
            raise KeyError(id)

    def __contains__(self, id):
        return id in self.__ids

    def __iter__(self):
        return self.__components.__iter__()

    def __len__(self):
        return self.__components.__len__()

    def __repr__(self):
        return "<%s>" % (self.__class__.__name__)
