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

from pytilities.event import (
    DispatcherSwitch, Dispatcher, UnsupportedEventError, RestrictedDispatcher)
from .helpers import Listener

class InitTestCase(unittest.TestCase):
    def test_main(self):
        self.d = Dispatcher()
        self.d.register_events("a", "b")
        self.d1 = RestrictedDispatcher(self.d, disallow=("b",))

        self.d2 = Dispatcher()
        self.d2.register_events("a", "c")

        self.d3 = Dispatcher()

        self.s = DispatcherSwitch()
        self.s.append_dispatchers(self.d1, self.d2, self.d3)

        self.l1 = Listener()
        self.s.add_handler("a", self.l1.handle_noarg)

        self.l2 = Listener()
        self.s.add_handler("c", self.l2.handle_noarg)

        self.l3 = Listener()
        self.d.add_handler("b", self.l3.handle_noarg)

        ###

        self.assert_(self.s.has_event("a"))
        self.assertFalse(self.s.has_event("b"))
        self.assert_(self.s.has_event("c"))
        
        self.assertRaises(UnsupportedEventError, 
                          self.s.add_handler,"b", self.l3.handle_noarg)

        self.d1.dispatch("a")
        self.assert_(self.l1.received_noarg)

        self.d2.dispatch("c")
        self.assert_(self.l2.received_noarg)

        self.d.dispatch("b")
        self.assert_(self.l3.received_noarg)

        ###

        self.s.remove_handler("a", self.l1.handle_noarg)

        self.d1.dispatch("a")
        self.assertFalse(self.l1.received_noarg)

        self.s.remove_handlers()

        self.d2.dispatch("c")
        self.assertFalse(self.l2.received_noarg)

        self.d.dispatch("b")
        self.assert_(self.l3.received_noarg)

