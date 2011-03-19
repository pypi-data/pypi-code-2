# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import copy
from functools import reduce

class Profile(object):

    """
    States what attributes to delegate, and to which target attributes.
    """

    def __init__(self):
        self.__readables = {}
        self.__writables = {}
        self.__deletables = {}

    def has_readable(self, attribute):
        """
        Check for read-access mapping of attribute

        :return: True if the mapping exists
        """
        return attribute in self.__readables

    def has_writable(self, attribute):
        """
        Check for write-access mapping of attribute

        :return: True if the mapping exists
        """
        return attribute in self.__writables

    def has_deletable(self, attribute):
        """
        Check for delete-access mapping of attribute

        :return: True if the mapping exists
        """
        return attribute in self.__deletables

    def get_readable(self, attribute):
        """
        Get the mapped value of a readable attribute

        :rtype: string
        """
        return self.__readables[attribute]

    def get_writable(self, attribute):
        """
        Get the mapped value of a writable attribute

        :rtype: string
        """
        return self.__writables[attribute]

    def get_deletable(self, attribute):
        """
        Get the mapped value of a deletable attribute

        :rtype: string
        """
        return self.__deletables[attribute]

    def __are_conflict_free(self, other):
        '''
        :return: True if mappings of self don't conflict with those of other
        '''
        # check for conflicts: intersect keys, then see whether intersections
        # map to the same values
        # If you get an assertion failure about this, then you should check
        # your bases to see if any of them map an attribute differently
        # e.g. with profiles a, b and attribute x: a.x should map to the same
        # value as b.x
        return reduce(lambda x, y: x and y,
                      (reduce(lambda x,y: x and y,
                              (a[key] == b[key]
                              for key 
                              in set(a) & set(b)),
                              True)
                      for a, b
                      in zip((self.__readables, self.__writables,
                             self.__deletables),
                            (other.__readables, other.__writables,
                             other.__deletables))),
                      True)

    # the | operator
    def __or__(self, other):
        '''See __ior__'''
        p = self.copy()
        p |= other
        return p

    def __ior__(self, other):
        """
        union of this profile and the other

        :param other: the other profile
        :type other: Profile

        :Preconditions: 1. The mappings of the two profiles musn't conflict. Two profiles
           conflict when they have at least one mapping with the same source
           name, but a different target name.
        """
        assert self.__are_conflict_free(other), \
            "Profiles have conflicting mappings, can't take union"

        # no conflicts, go ahead and update
        self.__readables.update(other.__readables)
        self.__writables.update(other.__writables)
        self.__deletables.update(other.__deletables)
        return self
    
    def __and__(self, other):
        p = self.copy()
        p &= other
        return p

    def __iand__(self, other):
        """
        intersection of this profile and the other

        :param other: the other profile
        :type other: Profile

        :Preconditions: 1. The mappings of the two profiles musn't conflict. Two profiles
            conflict when they have at least one mapping with the same source
            name, but a different target name.
        """

        assert self.__are_conflict_free(other), \
            "Profiles have conflicting mappings, can't take union"

        # no conflicts, go ahead and update
        for a, b in zip(
            (self.__readables, self.__writables, self.__deletables),
            (other.__readables, other.__writables, other.__deletables)):
            for key in tuple(a.keys()):
                if key not in b:
                    del a[key]

        return self

    
    def __sub__(self, other):
        p = self.copy()
        p -= other
        return p

    def __isub__(self, other):
        """
        difference of this profile and the other

        :param other: the other profile
        :type other: Profile
        """

        for a, b in zip(
            (self.__readables, self.__writables, self.__deletables),
            (other.__readables, other.__writables, other.__deletables)):
            for key in tuple(a.keys()):
                if key in b:
                    del a[key]

        return self

    
    def __xor__(self, other):
        p = self.copy()
        p ^= other
        return p

    def __ixor__(self, other):
        """
        symetric difference of this profile and the other

        :param other: the other profile
        :type other: Profile
        """
        
        # get the intersection of keys
        inter_readables = set(self.__readables.keys()) \
                         & set(other.__readables.keys())
        inter_writables = set(self.__writables.keys()) \
                         & set(other.__writables.keys())
        inter_deletables = set(self.__deletables.keys()) \
                         & set(other.__deletables.keys())

        # or the two together
        self.__readables.update(other.__readables)
        self.__writables.update(other.__writables)
        self.__deletables.update(other.__deletables)

        # remove the intersection
        for a, b in zip(
            (self.__readables, self.__writables, self.__deletables),
            (inter_readables, inter_writables, inter_deletables)):
            for key in tuple(a.keys()):
                if key in b:
                    del a[key]

        return self

    def remove_mappings(self, modifiers, *names):
        """
        Remove attribute mappings
        
        :param modifiers: 
            the types of delegation access to the target. Valid modifiers
            are combinations of:
                
            - 'r': read
            - 'w': write
            - 'd': delete
        :type modifiers: string

        :param names: source names of the attribute names to remove
        :type names: (string...)
        """

        for name in names:
            assert isinstance(name, str), \
                    "Invalid arguments: names should be list of strings: %s" \
                    % (names)

        for name in names:
            if "r" in modifiers:
                self.__readables.pop(name)

            if "w" in modifiers:
                self.__writables.pop(name)

            if "d" in modifiers:
                self.__deletables.pop(name)


    def add_mappings(self, modifiers, *names, **mapped_names):
        """
        Map source to target attribute names, for delegation.
        
        :param modifiers: 
            the types of delegation access to the target. Valid modifiers
            are combinations of:
                
            - 'r': read
            - 'w': write
            - 'd': delete
        :type modifiers: string

        :param names: source names of the attribute names to delegate. The target attribute
            name is the same as `source_name`. This is the same as adding a
            {source_name : source_name} mapping, using the mapped_names
            argument.
        :type names: (string...)

        :param mapped_names: names of source and target attributes to map and delegate.

            target_name will be mangled if they have a __ prefix.
            Mangling will occur every time it is delegated to, so you can
            change the target object any time.
        :type mapped_names: {source_name of string : target_name of string}
        """
        for name in names:
            assert isinstance(name, str), (
                "Invalid arguments: names should be list of strings. Got: %s" %
                names)

        for key, name in mapped_names.items():
            assert isinstance(key, str) and \
                    isinstance(name, str), \
                    "Invalid arguments: mapped_names should be dict of " + \
                    "string:string. Got: %s" % mapped_names

        if "r" in modifiers:
            self.__readables.update(zip(names, names), **mapped_names)

        if "w" in modifiers:
            self.__writables.update(zip(names, names), **mapped_names)

        if "d" in modifiers:
            self.__deletables.update(zip(names, names), **mapped_names)

    def copy(self):
        return copy.deepcopy(self)

    @property
    def readables(self):
        '''
        Get all readable attributes

        :return: (attribute_name, ...)
        :rtype: iter(str, ...)
        '''
        return self.__readables.keys()

    @property
    def writables(self):
        '''
        Get all writables attributes

        :return: (attribute_name, ...)
        :rtype: iter(str, ...)
        '''
        return self.__writables.keys()

    @property
    def deletables(self):
        '''
        Get all deletables attributes

        :return: (attribute_name, ...)
        :rtype: iter(str, ...)
        '''
        return self.__deletables.keys()

    @property
    def attributes(self):
        '''
        Get all attributes, no matter what access they provide

        :return: (attribute_name, ...)
        :rtype: iter(str, ...)
        '''
        return self.readables + self.writables + self.deletables

    def __str__(self):
        return 'Profile: r: %s, w: %s, d: %s' % (self.__readables,
                                                 self.__writables,
                                                 self.__deletables)

