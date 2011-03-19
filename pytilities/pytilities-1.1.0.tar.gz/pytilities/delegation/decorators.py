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

import logging
from collections import defaultdict

from pytilities import get_annotations
from . import Profile

# logging stuff
_logger = logging.getLogger("pytilities.delegation")

def profile_carrier(cls = None):
    '''
    Sets an attribute_profiles attribute on the class.

    The attribute_profiles attribute is a dict with profiles generated from
    `in_profile` annotations found on class attributes. It has profile names of
    type str as key and the respective profile as value.
    '''
    if cls is None:
        return profile_carrier

    # the resulting dict of profiles
    profiles = defaultdict(Profile)

    # look for delegated annotations
    for name, attribute in cls.__dict__.items():
        annotations = get_annotations(attribute, create=False)
        if annotations and 'profiles' in annotations:
            profile_data = annotations['profiles']
            for profile_name, modifiers in profile_data.items():
                profiles[profile_name].add_mappings(modifiers, name)

    # place it on the class
    setattr(cls, 'attribute_profiles', profiles)

    return cls

def in_profile(profile_name="default", modifiers="rwd"):
    """
    Includes the decorated attribute in the specified profile.

    :param profile_name: name of the `Profile` to add the attribute to
    :type profile_name: string
    :param modifiers: the kind of access to allow
    :type modifiers: str combination of r:read, w:write, d:delete (order is not
        important, but each modifier may appear at most once).
    """
    def _delegated(attribute):
        _logger.debug("%s += %s" % (profile_name, attribute))
        annotations = get_annotations(attribute, create=True)
        if not 'profiles' in annotations:
            annotations['profiles'] = {}

        annotations['profiles'][profile_name] = modifiers
        return attribute

    return _delegated

