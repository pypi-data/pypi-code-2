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

from pytilities.event import Dispatcher, UnsupportedEventError
from .helpers import Listener

class InitTestCase(unittest.TestCase):
    def setUp(self):
        self.l = Listener()
        self.ed = Dispatcher()

    def test_fail_no_events(self):
        self.assertFalse(self.ed.has_event("a"))
        self.assertRaises(UnsupportedEventError, self.ed.add_handler, "a", 
                          self.l.handle_noarg)
        self.assertRaises(UnsupportedEventError, self.ed.remove_handler, "a", 
                          self.l.handle_noarg)
        self.assertRaises(UnsupportedEventError, self.ed.dispatch, "a")

    def test_success(self):
        self.ed.register_events("a", "b")

        self.assert_(self.ed.has_event("b"))
        self.assert_(self.ed.has_event("b"))

        self.ed.add_handler("a", self.l.handle_noarg)
        self.ed.dispatch("a")

        #has handler a
        self.assertEquals(self.l.last, "noarg")

        self.ed.add_handler("b", self.l.handle_1arg)
        self.ed.dispatch("b", 5)

        #has handler a and b
        self.assertEquals(self.l.last, "1arg: 5")

        self.l.last = ""
        self.ed.remove_handler("a", self.l.handle_noarg)
        self.ed.dispatch("a")

        #has handler b
        self.assertNotEquals(self.l.last, "noarg")

        self.ed.add_handler("a", self.l.handle_noarg)
        self.ed.remove_handlers("a")
        self.ed.dispatch("a")

        self.assertNotEquals(self.l.last, "noarg")

        self.ed.dispatch("b", 5)

        self.assertEquals(self.l.last, "1arg: 5")

        self.l.last = ""
        self.ed.add_handler("a", self.l.handle_noarg)
        self.ed.remove_handlers()
        self.ed.dispatch("a")

        # has no handlers left
        self.assertNotEquals(self.l.last, "noarg")

        self.ed.dispatch("b", 5)

        self.assertNotEquals(self.l.last, "1arg: 5")

    def test_success_owner(self):
        self.ed.register_events("a", "b")

        self.ed.add_handler("a", self.l.handle_noarg, self.l)
        self.ed.dispatch("a")

        #has handler a
        self.assertEquals(self.l.last, "noarg")

        self.ed.add_handler("b", self.l.handle_1arg)
        self.ed.dispatch("b", 5)

        #has handler a and b
        self.assertEquals(self.l.last, "1arg: 5")

        self.l.last = ""
        self.ed.remove_handlers(owner=self.l)
        self.ed.dispatch("a")

        #has handler b
        self.assertNotEquals(self.l.last, "noarg")

        self.ed.dispatch("b", 5)

        self.assertEquals(self.l.last, "1arg: 5")

