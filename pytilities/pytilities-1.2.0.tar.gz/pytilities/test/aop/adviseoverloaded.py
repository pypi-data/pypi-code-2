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

import unittest

from pytilities import aop
from pytilities.aop import advisor, Aspect, AOPMeta
from pytilities.overloading import overloaded, Overload, Param
from pytilities.types import NumberType

class B(object, metaclass=AOPMeta):
    def __init_xy(self, x, y):
        return "xy", self, x, y

    def __init_storage(self, storage):
        return "storage", self, storage

    @overloaded((
        Overload(__init_xy,
            Param("x", NumberType, default=0),
            Param("y", NumberType, default=0)),
        Overload(__init_storage,
            Param("storage"))))
    def say_ni(self):
        """docstring is docstring"""
        pass

class AspectOverload(Aspect):

    '''
    Advise an overloaded attrib and do something different for different
    overloads
    '''

    def __init__(self):
        Aspect.__init__(self)
        self._advice_mappings['call', 'say_ni'] = self.advice

    def advice(self):
        args, kwargs = yield aop.arguments
        (name, f) = yield aop.advised_attribute
        kwargs, f = f.process_args(*args, kwargs=kwargs)
        if f.__name__ == '__init_xy':
            kwargs["x"] = 3
        else:
            kwargs['storage'] = 3

        yield aop.proceed(kwargs=kwargs)

aspect_overload = AspectOverload()

class OverloadTest(unittest.TestCase):

    '''Test aop works well together with our overloading lib'''

    def test_overload(self):
        aspect_overload.apply(B)

        b = B()
        self.assertEquals(b.say_ni(2, 4), ('xy', b, 3, 4))
        self.assertEquals(b.say_ni('uu'), ('storage', b, 3))

