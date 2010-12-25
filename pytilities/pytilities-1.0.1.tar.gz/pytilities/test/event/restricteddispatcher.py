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

from pytilities.event import Dispatcher, RestrictedDispatcher, UnsupportedEventError
from .helpers import Listener

class AllowTestCase(unittest.TestCase):
    '''Using the allow arg'''
    def setUp(self):
        self.l = Listener()

        d = Dispatcher()
        d.register_events("a", "b")
        self.ed = RestrictedDispatcher(d, allow=("b",))

    def test_fails(self):
        self.assertFalse(self.ed.has_event("a"))
        self.assertFalse(self.ed.has_event("c"))
        self.assertRaises(UnsupportedEventError, self.ed.add_handler, "a", 
                          self.l.handle_noarg)
        self.assertRaises(UnsupportedEventError, self.ed.remove_handler, "a", 
                          self.l.handle_noarg)
        self.assertRaises(UnsupportedEventError, self.ed.dispatch, "a")

    def test_success(self):
        self.assert_(self.ed.has_event("b"))

        self.ed.add_handler("b", self.l.handle_noarg)
        self.ed.dispatch("b")

        #has handler b
        self.assertEquals(self.l.last, "noarg")

class DisallowTestCase(unittest.TestCase):
    '''Using the disallow arg'''
    def setUp(self):
        self.l = Listener()

        d = Dispatcher()
        d.register_events("a", "b")
        self.ed = RestrictedDispatcher(d, disallow=("a",))

    def test_fails(self):
        self.assertFalse(self.ed.has_event("a"))
        self.assertFalse(self.ed.has_event("c"))
        self.assertRaises(UnsupportedEventError, self.ed.add_handler, "a", 
                          self.l.handle_noarg)
        self.assertRaises(UnsupportedEventError, self.ed.remove_handler, "a", 
                          self.l.handle_noarg)
        self.assertRaises(UnsupportedEventError, self.ed.dispatch, "a")

    def test_success(self):
        self.assert_(self.ed.has_event("b"))

        self.ed.add_handler("b", self.l.handle_noarg)
        self.ed.dispatch("b")

        #has handler b
        self.assertEquals(self.l.last, "noarg")

