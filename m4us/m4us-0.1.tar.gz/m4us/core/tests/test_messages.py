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


"""Tests for m4us.core.messages."""


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
import strait

#---  Project imports
from . import support
## pylint: disable=E0611
from .. import messages, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Support classes

class CheckIMessageFactoryTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    #---  Test case settings

    factory_interfaces = (interfaces.IMessageFactory,)

    #---  Tests

    def test_init_should_set_keyword_arguments_as_attributes(self):
        message = self.make_object(foo='bar', bat='baz')
        self.assert_true(hasattr(message, 'foo'))
        self.assert_equal(message.foo, 'bar')
        self.assert_true(hasattr(message, 'bat'))
        self.assert_equal(message.bat, 'baz')
        for key, value in self.factory_kwargs:
            self.assert_true(hasattr(message, key))
            self.assert_equal(getattr(message, key), value)


class CheckIMessgeTrait(object):

    #---  Test case settings

    object_interfaces = (interfaces.IMessage,)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------

STANDARD_MESSAGES_TRAITS = (
  CheckIMessageFactoryTrait,
  CheckIMessgeTrait,
)


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------

#---  Test classes

class TestMessage(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_MESSAGES_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = messages.Message


class TestShutdown(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_MESSAGES_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = messages.Shutdown
    object_interfaces = CheckIMessgeTrait.object_interfaces + \
      (interfaces.IShutdown,)


class TestProducerFinished(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_MESSAGES_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = messages.ProducerFinished
    object_interfaces = CheckIMessgeTrait.object_interfaces + \
      (interfaces.IShutdown, interfaces.IProducerFinished)


#---Late Module initialization-------------------------------------------------
