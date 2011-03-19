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

class DescriptorTestBase(unittest.TestCase):

    def setUp(self):
        class A(object): pass
        self.a = A()

        self.xprop = property(
            self.property_part('get'),
            self.property_part('set'),
            self.property_part('delete'))

        self.last_access = 'not accessed'
        self.last_arguments = None

    def when_use_descriptor(self, descriptor):
        class Holder(object):
            x = descriptor

        self.holder = Holder()

    def property_part(self, access):
        def f(*args):
            self.last_access = access
            self.last_arguments = args, {}
        return f

    def then_binding_should_work(self, obj):
        self.then_get_works(obj)
        self.then_set_works(obj)
        self.then_delete_works(obj)

    def then_get_works(self, obj):
        self.when_get()
        self.then_last_access_is('get')
        self.then_last_args_is(obj)

    def then_set_works(self, obj):
        self.when_set()
        self.then_last_access_is('set')
        self.then_last_args_is(obj, 2)

    def then_delete_works(self, obj):
        self.when_delete()
        self.then_last_access_is('delete')
        self.then_last_args_is(obj)

    def when_get(self):
        self.holder.x

    def when_set(self):
        self.holder.x = 2

    def when_delete(self):
        del self.holder.x

    def then_last_access_is(self, access):
        self.assertEqual(access, self.last_access)

    def then_last_args_is(self, *args):
        self.assertEqual((args,{}), self.last_arguments)

