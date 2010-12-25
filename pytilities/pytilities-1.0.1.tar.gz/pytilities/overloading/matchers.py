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

def matches_everything(value):
    """A matcher that always returns true
    """
    return True

def matches_type(*types):
    """A matcher that matches values which are instances of any of given types
    types: -- collection of types
    """
    def matcher(value):
        for type_ in types:
            if isinstance(value, type_):
                return True

        return False

    return matcher

def matches_all(*matchers):
    """A matcher that matches values which match all given matchers
    matchers: -- collection of matcher functions
    """
    def matcher(value):
        for matcher in matchers:
            if not matcher(value):
                return False

        return True

    return matcher

def matches_any(*matchers):
    """A matcher that matches values which are instances of any of given types
    matchers: -- ordered sequence of matcher functions
    """
    def matcher(value):
        for matcher in matchers:
            if matcher(value):
                return True

        return False

    return matcher

def matches_none(*matchers):
    """A matcher that matches values which are instances of any of given types
    matchers: -- collection of matcher functions
    """
    def matcher(value):
        for matcher in matchers:
            if matcher(value):
                return False

        return True

    return matcher

