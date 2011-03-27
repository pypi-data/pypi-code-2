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

"""
Various decorators to ease delegation
"""

__docformat__ = 'reStructuredText'

from pytilities import get_annotations

def mapped_class(cls = None):
    ''' Class decorator, required by `mapped` to work '''
    if cls is None:
        return mapped_class

    # look for and process annotations
    for attr_name, attr_value in cls.__dict__.items():
        annotations = get_annotations(attr_value, create=False)
        if annotations and 'mappings' in annotations:
            for mapping, accesses in annotations['mappings']:
                for access in accesses:
                    mapping[access, attr_name] = attr_name

    return cls

def mapped(mapping, *accesses):
    """
    Includes the decorated attribute in the specified mapping.

    The class on which the attribute resides, must be decorated with
    mapped_class.

    It maps according to: mapping[access, attr_name] = attr_name

    :param mapping: mapping instance to map new mapping with
    :type mapping: MutableMapping
    :param accesses: the kind of access to map. Default is ('get', 'set',
        'delete')
    :type accesses: tuple
    """
    if not accesses:
        accesses = ('get', 'set', 'delete')

    def _mapped(attribute):
        annotations = get_annotations(attribute, create=True)
        if not 'mappings' in annotations:
            annotations['mappings'] = []

        annotations['mappings'].append((mapping, accesses))
        return attribute

    return _mapped

