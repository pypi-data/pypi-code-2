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

""" Collection of functions that test for a particular condition """

import re

def is_iterable(obj):
    '''
    Test if something is iterable

    :param obj: any object
    '''
    return hasattr(obj, "__iter__")

def is_public(name):
    '''
    Test if name corresponds to a public attribute

    Names that do not start with '_' are public.

    :param name: Attribute name to test
    :type name: string
    '''
    return not name.startswith('_')

def is_protected(name):
    '''
    Test if name corresponds to a protected attribute

    Protected attribute names start '_', but don't contain '__'.

    :param name: Attribute name to test
    :type name: string
    '''
    return name.startswith('_') and not '__' in name

def is_private(name):
    '''
    Test if name corresponds to a private attribute

    Private attribute names are of format __name or _SomeClass_name

    :param name: Attribute name to test
    :type name: string
    '''
    return re.match('^(_[A-Z][^_]*)?__[a-zA-Z0-9]+$', name) is not None

def is_special(name):
    '''
    Test if name corresponds to a special attribute

    Special attribute names start and end with '__'.

    :param name: Attribute name to test
    :type name: string
    '''
    return name.startswith('__') and name.endswith('__')

