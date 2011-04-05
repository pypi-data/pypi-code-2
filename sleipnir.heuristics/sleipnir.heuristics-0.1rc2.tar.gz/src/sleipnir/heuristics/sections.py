#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
TSP Sections

Describes a Internal representation of a TSP problem. Tighly based on
TSPlib problem format description. Hopefully, it will allow to be used
for other formats
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "22 January 2010"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from oset import oset as OrderedSet
from itertools import ifilter

__all__ = ['SectionFactory']

# Project requirements
from sleipnir.core.event import Event
from sleipnir.core.factory import AbstractFactory
# local submodule requirements


class SectionError(Exception):
    """section exception"""


#pylint: disable-msg=R0903,W0232,E1101
class SectionFactory(AbstractFactory):
    """
    Allows to internally build a set of sections from passed args
    """


class MetaSection(type):
    """Section Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Section"):
            SectionFactory.get_instance().registry((name, mcs))


#pylint: disable-msg=R0903
class AbstractSection(object):
    """Base class to be used (optionally) by all sections"""

    __metaclass__ = MetaSection

    #pylint: disable-msg=W0613
    def __init__(self, **kwargs):
        super(AbstractSection, self).__init__()

    @classmethod
    def can_handle(cls, *args, **kwargs):
        """
        Advise if it's a valid class for arguments pased to the method
        """
        return False


class ParentSection(AbstractSection):
    """A section which has a parent"""

    def __init__(self, **kwargs):
        super(ParentSection, self).__init__(**kwargs)
        self.__parent = kwargs.get('parent', None)
        if hasattr(self.parent, 'add'):
            self.parent.add(self)

    def __eq__(self, other):
        return type(self) == type(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def parent(self):
        """Section's parent"""
        return self.__parent

    #pylint:disable-msg=E0102,E1101
    @parent.setter
    def parent(self, value):
        """Set section's parent"""
        self.__parent = value

    @property
    def root(self):
        """Gets root parent"""
        if self.parent is not None:
            parent = self.parent
            while parent.parent is not None:
                parent = parent.parent
            return parent
        return None


class IterableSection(AbstractSection):
    """
    An iterator for sections

    It conects to 'update' events from parent, if any, and update
    dinamically to reflect parent changes
    """

    def __init__(self, **kwargs):
        self.__itertype = kwargs.get('type', None)
        self.__ancestor = kwargs.get('parent', None)
        self.__chfilter = kwargs.get('children', None)
        self.__children = None

        # Connect to parent to be notified about parent updates.
        # If so, update self.__children accordingly.
        if hasattr(self.__ancestor, "__iadd__") and self.__chfilter:
            self.__ancestor.events['updated'].connect(self.__update_event)

        # Call ancestors
        super(IterableSection, self).__init__(**kwargs)

    def __getattr__(self, name):
        # This allow us to return a ancestor creator functio
        if self.__ancestor is not None and self.__itertype:
            action = name + "_" + self.__itertype
            action = getattr(self.__ancestor, action, None)
            action = action or getattr(self.__ancestor, name, None)
            if action and callable(action):
                return action

        # return child whose name matchs attribute (name)
        for child in self.children:
            if child.name.lower() == name:
                return child

        # Not Found? raise Error
        raise AttributeError(name)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        for child in self.children:
            yield child

    def __getitem__(self, key):
        try:
            if isinstance(key, str):
                return getattr(self, key)
            return self.children[key]
        except AttributeError:
            raise KeyError("Invalid key %s", key)

    def __call__(self, func):
        return [child(func) for child in self.children]

    def __update_event(self, child, ev_detail):
        """Handler for update events"""

        # We don't fire any event here because IterableSection
        # has Weak References to childs.
        if self.__chfilter(child):
            if ev_detail == 'added':
                self.children.add(child)
            else:
                self.children.remove(child)

    @property
    def children(self):
        """Iterator section elements"""

        if self.__children is None:
            children = self.__children = OrderedSet()
            if self.__ancestor is not None and self.__chfilter:
                children = OrderedSet([c for c in self.__ancestor if self.__chfilter(c)])
                self.__children = children
        return self.__children

    @property
    def type(self):
        """Iterator valid child type"""

        return self.__itertype

    def get(self, key, retval=None):
        """Iterator accesor"""

        return self[key] if key in self else retval


class ElementSection(ParentSection):
    """
    An element sections is a part of a TSP problem which provides
    contents, not structure. Currently, thres four min types of
    sections
    """

    #pylint: disable-msg=W0622
    def __init__(self, value, type=None, **kwargs):
        self._value, self._type = value, type
        super(ElementSection, self).__init__(**kwargs)

    def __call__(self, func):
        return func(self._value)

    def __eq__(self, other):
        return self._value == other.value and self._type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def type(self):
        """Returns section type"""
        return self._type

    @property
    def value(self):
        """Returns true value"""
        return self._value


class ContainerSection(ParentSection):
    """An abstract class to implement containers"""

    def __init__(self, **kwargs):
        # Define Notification Events
        self.events = {
            'updated': Event(
                "updated", ["added", "removed", None], self)
            }
        self._children = OrderedSet()
        # Store Here Container Iterators
        self._cache = {}
        # Add children to the container ant notify accordingly
        for child in kwargs.get('children', []):
            assert child.parent is None
            self.add(child)
        #now call parent
        super(ContainerSection, self).__init__(**kwargs)

    def __eq__(self, other):
        if not super(ContainerSection, self).__eq__(other):
            return False
        # Two cointainers are NOT EQUAL if childrens aren't sorted
        return self._children == other._children

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        for child in self._children:
            yield child

    def __iadd__(self, leaf):
        if leaf not in self._children:
            self.events["updated"].emit_detail("added", leaf)
            self._children.add(leaf)
            leaf.parent = self
        return leaf

    def __isub__(self, leaf):
        leaf.parent = None
        self._children.remove(leaf)
        self.events["updated"].emit_detail("removed", leaf)
        # Remove itself from parent if it doesn't
        # contain any more children inside(GC)
        if len(self) == 0 and self.parent:
            self.parent.remove(self)
        return leaf

    @property
    def children(self):
        """return section leafs"""

        return self._children

    def add(self, leaf):
        """Add a section to the container"""

        return self.__iadd__(leaf)

    def remove(self, leaf):
        """Removes a section from the container"""

        return self.__isub__(leaf)


class ContainerElementSection(ElementSection, ContainerSection):
    """
    A section element which could have other elements inside like
    comments or othe ElementSections
    """

    def __init__(self, *args, **kwargs):
        self._name = None
        super(ContainerElementSection, self).__init__(*args, **kwargs)


    def __ne__(self, other):
        return not self.__eq__(self)

    @property
    def filters(self):
        """
        Used to return only a subset of childs which mach any of the
        filter properties. Tipically, it's implemented as a dict,
        where key is accesor and value is leaf type
        """

        # pylint: disable-msg=R0201
        raise AttributeError('filters')

    @property
    def name(self):
        """
        Sugar name to allow section accessors to access to a section
        header or content.

        It removes from name reserved keywords _TYPE and _SECTION if
        present
        """

        # pylint: disable-msg=R0201
        raise AttributeError('name')

    def __getattr__(self, name):
        def __filter(name):
            """A filter for iterables"""
            types = self.filters.get(name)
            return lambda x: getattr(x, "type", None) == types
        if name in self.filters:
            if name not in self._cache:
                self._cache[name] = IterableSection(
                    parent=self,
                    type=self.filters[name],
                    children=__filter(name))
            return self._cache[name]

        if name.startswith('create_'):
            create_type = name.split("_", 1)[1]
            factory = SectionFactory.get_instance()
            return lambda x: factory.create(x, type=create_type, parent=self)

        raise AttributeError(name)


class SectionTSP(ContainerSection):
    """A section which describes a TSP problem"""

    #pylint:disable-msg=C0103
    class __TSPIterableSection(IterableSection):
        """Private Iterator to handle which TSP problem structure"""

        def update_event(self, child, ev_detail):
            """handler to update events"""

            def __update(leaf):
                """recursive method to update iterator"""

                if self.type == leaf.type:
                    if ev_detail == 'added':
                        self.children.add(leaf)
                    else:
                        self.children.remove(leaf)
            if hasattr(child, "type"):
                __update(child)
            else:
                for leaf in child:
                    __update(leaf)
                if child.events['updated']:
                    if ev_detail == 'added':
                        child.events['updated'].connect(self.update_event)
                    else:
                        child.events['updated'].remove(self.update_event)

    def __init__(self, **kwargs):
        super(SectionTSP, self).__init__(**kwargs)
        # Initiate Caches
        for key in ('comments', 'sections', 'contents',):
            self._cache[key] = self.__TSPIterableSection(
                parent=self, type=key[:-1])
            self.events['updated'].connect(self._cache[key].update_event)

    def __getattr__(self, name):
        # return iterable if ask for a collection
        if name in self._cache:
            return self._cache[name]

        # handle children creation/destruction
        if name.startswith('create_'):
            create_type = name.split("_", 1)[1]
            return lambda x: self.__create(x, str(create_type))

        # handle special case self.<name> to access a section
        for child in ifilter(lambda x: isinstance(x, SectionContainer), self):
            if child.name and child.name.lower() == name:
                return child

        raise AttributeError(name)

    def __isub__(self, value):
        for cnt in ifilter(lambda x: value in x, self):
            return cnt.remove(value)
        return super(SectionTSP, self).__isub__(value)

    def __iadd__(self, value):
        if not hasattr(value, 'type') or value.type in ('comment'):
            return super(SectionTSP, self).__iadd__(value)

        if value.type not in ('section', 'content'):
            raise TypeError("Unsupported type for SectionTSP % s", type(value))

        valtype = value.type
        factory = SectionFactory.get_instance()
        cntname = value.name.lower()
        cnt = getattr(self, cntname, None) or factory.create(parent=self)
        if cnt.name == value.name and getattr(cnt, valtype, None) is not None:
            raise SectionError("Header '%s' (%s) exists", value, valtype)
        return cnt.add(value)

    def __create(self, value, stype):
        """An internal sugar to create leaf sections at runtime"""

        factory = SectionFactory.get_instance()
        # comments
        if stype in ('comment',):
            return factory.create(value, type='comment', parent=self)
        # headers
        if stype in ('section', 'content',):
            return self.add(factory.create(value, type=stype))

        # Fail
        raise NotImplementedError(stype)

    @classmethod
    def can_handle(cls, *args, **kwargs):
        return True if not args and not kwargs else False


class SectionContainer(ContainerSection):
    """
    A part of a TSP problem which provides structure, it tipically
    contains other containers or elements. It NEVER has data
    """

    def __init__(self, **kwargs):
        super(SectionContainer, self).__init__(**kwargs)

    def __getattr__(self, name):
        if name in ('section', 'content',):
            for child in self._children:
                if getattr(child, "type", None) == name:
                    return child
        raise AttributeError(name)

    @property
    def name(self):
        """Section's name"""

        for child in self._children:
            if getattr(child, "name", None):
                return child.name
        return None

    @classmethod
    def can_handle(cls, *args, **kwargs):
        return isinstance(kwargs.get('parent', None), SectionTSP) \
           and kwargs.get('type', None) == None


class SectionHeader(ContainerElementSection):
    """
    A section container wich could contains comments or header values
    """

    def __init__(self, *args, **kwargs):
        self.__filters = {
            'values': 'sec_value',
            'comments': 'comment',
            }
        super(SectionHeader, self).__init__(*args, **kwargs)

    @property
    def filters(self):
        return self.__filters

    @property
    def name(self):
        if self._name is None and self._value:
            value = self._value
            self._name = value[:-5] if value.endswith('_TYPE') else value
        return self._name

    @classmethod
    def can_handle(cls, *args, **kwargs):
        return kwargs.get('type', None) in ('section',)


class SectionContent(ContainerElementSection):
    """
    A section container which stores comments or content values
    """

    def __init__(self, *args, **kwargs):
        self.__filters = {
            'values': 'content_value',
            'comments': 'comment',
            }
        super(SectionContent, self).__init__(*args, **kwargs)

    @property
    def filters(self):
        return self.__filters

    @property
    def name(self):
        if self._name is None and self._value:
            value = self._value
            self._name = value[:-8] if value.endswith('_SECTION') else value
        return self._name

    @classmethod
    def can_handle(cls, *args, **kwargs):
        return kwargs.get('type', None) in ('content',)


class SectionValue(ContainerElementSection):
    """A section to albergate value sets"""

    def __init__(self, *args, **kwargs):
        self.__filters = {
            'comments': 'comment',
            }
        super(SectionValue, self).__init__(*args, **kwargs)

    @property
    def filters(self):
        return self.__filters

    @classmethod
    def can_handle(cls, *args, **kwargs):
        return kwargs.get('type', None) in ('sec_value', 'content_value',)


class SectionComment(ElementSection):
    """A section to represent a comment"""

    def __call__(self, func):
        return func(self._value)

    @classmethod
    def can_handle(cls, *args, **kwargs):
        if kwargs.get('type', None) in ('comment',):
            return True
        if len(args) > 0 and isinstance(args[0], (str, unicode,)):
            return True
