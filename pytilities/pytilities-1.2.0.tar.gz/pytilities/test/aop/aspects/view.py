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
from pytilities.aop.aspects import create_view
from pytilities.aop import Aspect

class ViewTest(unittest.TestCase):
    def test_all(self):
        obj = A()
        self.then_aspect_not_affects(obj) #sanity check
        self.then_attributes_are_reachable(obj)

        view = create_view(aspect)
        viewed_obj = view(obj)
        viewed_obj.x

        self.then_aspect_not_affects(obj)
        self.then_aspect_affects(viewed_obj)
        self.then_attributes_are_reachable(obj)
        self.then_attributes_are_reachable(viewed_obj)

    def then_aspect_not_affects(self, obj):
        aspect.reset()
        obj.x
        self.assertEquals(0, aspect.affectedGetAt)

    def then_aspect_affects(self, obj):
        aspect.reset()
        obj.x
        self.assertEquals(1, aspect.affectedGetAt)

    def then_attributes_are_reachable(self, obj):
        self.assertEquals(default_x, obj.x)


class A(object):

    @property
    def x(self):
        return default_x

default_x = 1

class AspectA(Aspect):

    def __init__(self):
        Aspect.__init__(self)
        self._advice_mappings['get', 'x'] = self._affect_get
        self.reset()

    def reset(self):
        self.affectedGetAt = 0

    def _affect_get(self):
        self.affectedGetAt = 1
        yield aop.proceed

aspect = AspectA()
