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

from pytilities.aop import AOPMeta
from pytilities.delegation import DelegationAspect

class Wrapper(object):
    def __init__(self, wrapped):
        self._wrapped = wrapped

class MetaWrapper(object, metaclass=AOPMeta):
    def __init__(self, wrapped):
        self._wrapped = wrapped

class A(object):
    @property
    def x(self):
        self.last_args = (self,)

    @x.setter
    def x(self, value):
        self.last_args = (self, value)

    @x.deleter
    def x(self):
        self.last_args = (self,)

    def f(*args):
        self = args[0]
        self.last_args = args

    def reset(self):
        self.last_args = None

class TestBase(unittest.TestCase):

    def setUp(self):
        self.a = A()
        self.Wrapper = Wrapper
        self.MetaWrapper = MetaWrapper

    def when_wrap(self, with_=('x', 'f'), wrapper=Wrapper):
        self.wrapper = wrapper(self.a)
        delegation_aspect = DelegationAspect(property(lambda s: s._wrapped),
                                             with_)
        delegation_aspect.apply(self.wrapper)

    def then_delegation_works(self):
        self.then_get_works()
        self.then_set_works()
        self.then_delete_works()

    def then_get_works(self):
        self.a.reset()
        self.when_get_property()
        self.assertEqual((self.a,), self.a.last_args)

        self.a.reset()
        self.when_get_function()
        self.assertEqual((self.a,), self.a.last_args)

    def then_set_works(self):
        self.a.reset()
        self.when_set()
        self.assertEqual((self.a, 1), self.a.last_args)

    def then_delete_works(self):
        self.a.reset()
        self.when_delete()
        self.assertEqual((self.a,), self.a.last_args)

    def when_get_property(self):
        self.wrapper.x

    def when_get_function(self):
        self.wrapper.f()

    def when_set(self):
        self.wrapper.x = 1

    def when_delete(self):
        del self.wrapper.x

    def then_get_fails(self):
        with self.assertRaises(Exception):
            self.then_get_works()

    def then_set_fails(self):
        with self.assertRaises(Exception):
            self.then_set_works()

    def then_delete_fails(self):
        with self.assertRaises(Exception):
            self.then_delete_works()
