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

from . import ImmutableAttributeException
from pytilities.aop import Aspect
from pytilities import aop
from pytilities.dictionary import FunctionMap

class ImmutableAspect(Aspect):
    '''
    Aspect that makes given attributes immutable.

    It will raise ImmutabileAttributeException when the value of one of the 
    immutable attributes changes by using one of its public attributes.

    It raises after the modification is done, it doesn't actually prevent it.

    Can only be applied to AOPMeta objects.
    '''

    def __init__(self, attributes):
        '''
        Create an `ImmutableAspect`.

        :param attributes: Attribute names whose setters to guard
        :type attributes: iter(str, ...)
        '''
        Aspect.__init__(self)
        self._advice_mappings = FunctionMap(self._mapper)
        self._undefined_keys = True
        self.attributes = attributes

    def _mapper(self, key):
        access, attribute_name = key
        return self._detect_change

    def _detect_change(self):
        with (yield aop.suppress_aspect):
            (obj, *args), kwargs = yield aop.arguments
            attribute_values = {attribute : getattr(obj, attribute) 
                                for attribute
                                in self.attributes}

            yield aop.proceed

            for attribute, value in attribute_values.items():
                if getattr(obj, attribute) != value:
                    raise ImmutableAttributeException(
                        "Tried to modify immutable attribute: %s" 
                        % attribute)

