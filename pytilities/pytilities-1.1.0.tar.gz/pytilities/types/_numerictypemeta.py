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

from pytilities.infinity import infinity, negative_infinity

class _NumericTypeMeta(type):
    def __instancecheck__(self, instance):
        try:
            float(instance)
            return True
        except (ValueError, TypeError):
            return instance in (infinity, negative_infinity)

    # inside meta classes, self refers to the class that has this meta as
    # metaclass
    def __subclasscheck__(self, subclass):
        """Note: returns false for a string as we can't tell whether it's
        numeric. Try to avoid subclass checks of numbers with strings.
        """
        if subclass is self:
            return True

        for type_ in (int, float, infinity.__class__,
                      negative_infinity.__class__):
            if issubclass(type_, subclass):
                return True

        return False
