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

import inspect
from pytilities.overloading import overloaded, Overload, Param

def get_attr_name(obj, value):
    '''
    Get name of attribute that has `value`, but bypass regular lookup.
    
    It checks __dict__s directly.

    Values are matched like: `v == value`

    :param obj: the object to start looking for the attr on
    :type obj: class
    :param value: value to look for
    :raise AttributeError: if attr wasn't found
    :return: attribute value as found in the __dict__
    '''
    for o in obj.__mro__:
        for name, v in o.__dict__.items():
            if v == value:
                return name
    else:
        raise AttributeError(name)

def get_attr_value(obj, name):
    '''
    Like getattr, but bypasses regular lookup.

    It checks __dict__s directly.

    :param obj: the object to start looking for the attr on
    :type obj: class
    :param name: name of the attribute to look for
    :type name: str
    :raise AttributeError: if attr wasn't found
    :return: attribute value as found in the __dict__
    '''
    for o in obj.__mro__:
        if name in o.__dict__:
            return o.__dict__[name]
    else:
        raise AttributeError(name)

def get_attr_value_or_none(obj, name):
    '''
    Like get_attr_value, but returns None if attr does not exist
    '''
    try:
        return get_attr_value(obj, name)
    except AttributeError:
        return None

def has_attr_name(obj, name):
    '''
    Like hasattr, but bypasses regular lookup.
    
    It checks __dict__s directly.

    :param obj: the object to start looking for the attr on
    :type obj: class
    :param name: name of the attribute to look for
    :type name: str
    :return: True if a dict contained name, False otherwise
    :rtype: bool
    '''
    try:
        get_attr_value(obj, name)
    except AttributeError:
        return False
    return True

def has_attr_value(obj, value):
    '''
    See if its dicts contain `value` as value, bypassing regular lookup.
    
    It checks __dict__s directly.

    :param obj: the object to start looking for the attr on
    :type obj: class
    :param value: value to look for
    :return: True if a dict.values contained value, False otherwise
    :rtype: bool
    '''
    try:
        get_attr_name(obj, value)
    except AttributeError:
        return False
    return True

def _mangle_str(cls_name, attribute):
    if attribute.startswith("__") and not attribute.endswith("__"):
        while cls_name.startswith('_'):
            cls_name = cls_name[1:]

        return "_" + cls_name + attribute
    else:
        return attribute

def _mangle_owner(owner, attribute):
    if inspect.isclass(owner):
        cls_name = owner.__name__
    else:
        cls_name = owner.__class__.__name__

    return _mangle_str(cls_name, attribute)

@overloaded((
    Overload(_mangle_str,
        Param("cls_name", str),
        Param("attribute")),
    Overload(_mangle_owner,
        Param("owner"),
        Param("attribute"))), False)
        
def mangle(owner, attribute):
    """
    Get the mangled name of an attribute
    
    :param owner: the instance/class to which the attribute belongs to or name
        of the class.
    :type owner: instance or class or str
    :param attribute: the attribute name to mangle
    :type attribute: string
    
    :return: mangled attribute, if it was private. Return unmangled otherwise.
    :rtype: string
    """

def get_annotations(obj, create = True):
    '''
    Get a mutable dict of annotations on an object.

    Changing values on the dict changes the annotations of the object.
    
    It's smart enough to handle properties, ... 

    :param obj: the object to look for annotations on
    :type obj: object
    :param create: if True, creates an annotations dict on the object if none
        was found
    :type create: bool
    :return: annotations of the object or None if no annotations were found and
        create is False
    :rtype: {object: object}
    '''
    try:
        return obj.__annotations__
    except AttributeError:
        # must be some class or annoying builtin then ;)
        if isinstance(obj, property):
            # just use its get function
            try:
                return obj.fget.__annotations__
            except AttributeError:
                # fine, no get func
                if hasattr(obj, 'fset'): # set func then?
                    return obj.fset.__annotations__
                elif hasattr(obj, 'fdel'): # del func??
                    return obj.fdel.__annotations__
        elif create:
            # try to set a new annotations attrib on the obj
            obj.__annotations__ = {}
            return obj.__annotations__

    # give up
    if create:
        raise AttributeError
    else:
        return None



