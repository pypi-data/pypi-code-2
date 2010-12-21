# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2010 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.


"""Tests for m4us.core.utils."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

#---  Third-party imports
import mock
import strait

#---  Project imports
from . import support
## pylint: disable=E0611
from .. import utils, messages, postoffices, exceptions
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Test classes

class TestEasyLink(support.TestCase):

    __metaclass__ = strait.include(support.CoreM4USTestSupportTrait)

    #---  Setup and teardown

    def setup(self):
        self.factory = utils.easy_link
        self.factory_args = tuple(self.make_mock_coroutines())

    #---  Support methods

    def make_mock_coroutines(self):
        return [mock.Mock() for _ in xrange(5)]

    #---  Tests

    def test_easy_link_should_link_outboxes_inboxes_signals_and_controls(self):
        coroutines = self.make_mock_coroutines()
        links = self.factory(*coroutines)
        self.assert_equal(len(links), (len(coroutines) - 1) * 2)
        for source, sink in zip(coroutines, coroutines[1:]):
            self.assert_in((source, 'outbox', sink, 'inbox'), links)
            self.assert_in((source, 'signal', sink, 'control'), links)

    def test_easy_link_should_return_links_compatible_with_ipostoffice(self):
        post_office = postoffices.PostOffice()
        links = self.make_object()
        with self.assert_not_raises(TypeError):
            with self.assert_not_raises(exceptions.LinkExistsError):
                post_office.link(*links)


class TestIsShutdown(support.TestCase):

    #---  Setup and teardown

    def setup(self):
        self.factory = utils.is_shutdown

    #---  Tests

    def test_is_shutdown_should_return_true_if_control_and_ishutdown(self):
        self.assert_true(self.factory('control', messages.Shutdown()))

    def test_is_shutdown_should_return_false_if_inbox_is_not_control(self):
        self.assert_false(self.factory('uncontrol', messages.Shutdown()))

    def test_is_shutdown_should_return_false_if_message_is_not_ishutdown(self):
        self.assert_false(self.factory('control', 'not shutdown'))

    def test_is_shutdown_should_allow_overriding_of_the_inbox_name(self):
        self.assert_true(self.factory('changed_inbox', messages.Shutdown(),
          expected_inbox='changed_inbox'))


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
