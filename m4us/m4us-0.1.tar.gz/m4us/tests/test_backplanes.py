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


"""Tests for m4us.backplanes."""


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
from ..core import api as core
## pylint: disable=E0611
from .. import interfaces, backplanes
## pylint: enable=E0611
from ..core.tests import (test_components, test_coroutines, test_exceptions,
  test_messages, support)


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class TestRegisterPublisher(support.TestCase):

    __metaclass__ = strait.include(
      *(test_messages.STANDARD_MESSAGES_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = backplanes.RegisterPublisher
    factory_kwargs = ((b'publisher', 'some publisher'),)
    object_interfaces = test_messages.CheckIMessgeTrait.object_interfaces + \
      (interfaces.IRegisterPublisher,)


class TestUnregisterPublisher(support.TestCase):

    __metaclass__ = strait.include(
      *(test_messages.STANDARD_MESSAGES_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = backplanes.UnregisterPublisher
    factory_kwargs = ((b'publisher', 'some publisher'),)
    object_interfaces = test_messages.CheckIMessgeTrait.object_interfaces + \
      (interfaces.IUnregisterPublisher,)


class TestNotRegisteredError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *test_exceptions.STANDARD_EXCEPTIONS_TRAITS)

    factory = backplanes.NotRegisteredError
    factory_kwargs = ((b'publisher', 'publisher'),)


class TestAlreadyRegisteredError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *test_exceptions.STANDARD_EXCEPTIONS_TRAITS)

    factory = backplanes.AlreadyRegisteredError
    factory_kwargs = ((b'publisher', 'publisher'),)


class TestBackplane(support.TestCase):

    __metaclass__ = strait.include(
      test_components.CheckComponentTrait,
      *(test_coroutines.STANDARD_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = backplanes.Backplane
    factory_interfaces = (interfaces.IBackplaneFactory,) + \
      test_coroutines.CheckICoroutineFactoryTrait.factory_interfaces
    object_interfaces = (interfaces.IBackplane,) + \
      test_coroutines.CheckICoroutineTrait.object_interfaces

    #---  Support methods

    def make_registration_message(self, publisher=None, _message_class=None):
        if publisher is None:
            publisher = 'some publisher'
        if _message_class is None:
            _message_class = backplanes.RegisterPublisher
        return ('control', _message_class(publisher=publisher))

    def make_unregistration_message(self, publisher=None):
        return self.make_registration_message(publisher,
          _message_class=backplanes.UnregisterPublisher)

    #---  Registration tests

    def test_backplane_should_accept_publisher_registration(self):
        backplane = self.make_object()
        registration_message = self.make_registration_message()
        result = backplane.send(registration_message)
        self.assert_is_none(result)

    def test_backplane_should_raise_alreadyregisterederror_if_registered(self):
        backplane = self.make_object()
        registration_message = self.make_registration_message()
        backplane.send(registration_message)
        with self.assert_raises(backplanes.AlreadyRegisteredError):
            backplane.send(registration_message)

    def test_backplane_should_accept_publisher_unregistration(self):
        backplane = self.make_object()
        registration_message = self.make_registration_message()
        unregistration_message = self.make_unregistration_message()
        backplane.send(registration_message)
        result = backplane.send(unregistration_message)
        self.assert_is_none(result)

    def test_backplane_should_raise_notregisterederror_if_not_registered(self):
        backplane = self.make_object()
        unregistration_message = self.make_unregistration_message()
        with self.assert_raises(backplanes.NotRegisteredError):
            backplane.send(unregistration_message)

    #---  Shutdown tests

    def test_backplane_should_not_emit_ishutdown_until_no_publishers(self):
        backplane = self.make_object()
        registration_message_1 = self.make_registration_message('p1')
        unregistration_message_1 = self.make_unregistration_message('p1')
        registration_message_2 = self.make_registration_message('p2')
        unregistration_message_2 = self.make_unregistration_message('p2')
        shutdown_message = ('control', core.Shutdown())
        backplane.send(registration_message_1)
        backplane.send(registration_message_2)
        for _ in xrange(5):
            result = backplane.send(shutdown_message)
            self.assert_is_none(result)
        backplane.send(unregistration_message_1)
        result = backplane.send(shutdown_message)
        self.assert_is_none(result)
        backplane.send(unregistration_message_2)
        # This is where we want the IShutdown messages to be emitted, not any
        # sooner.
        self.assert_coroutine_forwards_ishutdown_message(backplane,
          core.Shutdown())

    def test_backplane_should_not_shutdown_until_no_publishers(self):
        backplane = self.make_object()
        registration_message_1 = self.make_registration_message('p1')
        unregistration_message_1 = self.make_unregistration_message('p1')
        registration_message_2 = self.make_registration_message('p2')
        unregistration_message_2 = self.make_unregistration_message('p2')
        shutdown_message = ('control', core.Shutdown())
        backplane.send(registration_message_1)
        backplane.send(registration_message_2)
        backplane.send(shutdown_message)
        backplane.send(unregistration_message_1)
        backplane.send(shutdown_message)
        backplane.send(unregistration_message_2)
        # This is where we want the StopIteration, not any sooner.
        self.assert_coroutine_shuts_down_on_message(backplane, core.Shutdown())


class TestPublisher(support.TestCase):

    __metaclass__ = strait.include(
      test_components.CheckComponentTrait,
      *(test_coroutines.STANDARD_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = backplanes.Publisher
    object_interfaces = (core.INotLazy,) + \
      test_coroutines.CheckICoroutineTrait.object_interfaces

    #---  Support methods

    def assert_first_message_is_iregisterpublisher(self, publisher,
      message=None):
        if message is None:
            message = self.get_messages()[0]
        outbox, response = publisher.send(message)
        self.assert_equal(outbox, 'signal')
        self.assert_true(interfaces.IRegisterPublisher(response, False))

    def assert_nth_post_shutdown_message_interface(self, publisher,
      message_count, shutdown_message, expected_interface):
        self.assert_first_message_is_iregisterpublisher(publisher)
        for _ in xrange(message_count):
            outbox, message = publisher.send(('control', shutdown_message))
        self.assert_equal(outbox, 'signal')
        self.assert_true(expected_interface(message, False),
          'Message {0} after IShutdown was not an {1}.'.format(message_count,
          expected_interface.getName()))

    #---  Init tests

    def test_component_should_initialize_the_contained_coroutine(self):
        # Overridden from test_components.CheckComponentTrait
        publisher = self.make_object()
        self.assert_true(hasattr(publisher, '_coroutine'))
        self.assert_first_message_is_iregisterpublisher(publisher)

    #---  Main tests

    def test_main_should_emit_iregisterpublisher_as_first_message(self):
        publisher = self.make_object()
        self.assert_first_message_is_iregisterpublisher(publisher)

    def test_main_should_emit_first_incomming_message_as_second_message(self):
        publisher = self.make_object()
        messages = self.get_messages()
        expected_response = self.get_responses()[0]
        self.assert_first_message_is_iregisterpublisher(publisher, messages[0])
        response = publisher.send(messages[1])
        self.assert_equal(response, expected_response)

    def test_main_should_emit_previous_message_first_on_ishutdown(self):
        publisher = self.make_object()
        message = self.get_messages()[0]
        expected_response = self.get_responses()[0]
        shutdown_message = ('control', core.Shutdown())
        self.assert_first_message_is_iregisterpublisher(publisher, message)
        response = publisher.send(shutdown_message)
        self.assert_equal(response, expected_response)

    def test_main_should_emit_iunregisterpublisher_second_on_ishutdown(self):
        publisher = self.make_object()
        self.assert_nth_post_shutdown_message_interface(publisher, 2,
          core.Shutdown(), interfaces.IUnregisterPublisher)

    def test_icoroutine_should_send_and_receive_messages(self):
        # Overridden method from test_coroutines.CheckICoroutineTrait
        publisher = self.make_object()
        messages = self.get_messages()
        responses = self.get_responses()
        self.assert_first_message_is_iregisterpublisher(publisher, messages[0])
        # [(m2, r1), (m1, r2), (m2, r1)]
        for message, response in zip((messages * 2)[1:], responses * 2):
            self.assert_equal(publisher.send(message), response)

    def test_icoroutine_should_forward_the_shutdown_message(self):
        # Overridden method from test_coroutines.CheckStandardMessagesTrait.
        # _main should emit IShutdown as the third message after the incomming
        # IShutdown
        publisher = self.make_object()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          core.Shutdown(), core.IShutdown)

    def test_icoroutine_should_shutdown_on_shutdown_message(self):
        # Overridden method from test_coroutines.CheckStandardMessagesTrait.
        # _main should raise StopIteration after IShutdown is emitted.
        publisher = self.make_object()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          core.Shutdown(), core.IShutdown)
        with self.assert_raises(StopIteration):
            publisher.send(('signal', core.Shutdown()))

    def test_icoroutine_should_forward_the_producerfinished_message(self):
        # Overridden method from test_coroutines.CheckStandardMessagesTrait.
        publisher = self.make_object()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          core.ProducerFinished(), core.IProducerFinished)

    def test_icoroutine_should_shutdown_on_producerfinished_message(self):
        # Overridden method from test_coroutines.CheckStandardMessagesTrait.
        publisher = self.make_object()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          core.ProducerFinished(), core.IProducerFinished)
        with self.assert_raises(StopIteration):
            publisher.send(('signal', core.Shutdown()))

    def test_main_should_ignore_none_messages_on_control_inbox(self):
        publisher = self.make_object()
        message = self.get_messages()[0]
        publisher.send(('control', None))
        result = publisher.send(message)
        self.assert_is_none(result)


class TestPublishTo(support.TestCase):

    __metaclass__ = strait.include(support.CoreM4USTestSupportTrait)

    #---  Setup and teardown

    def setup(self):
        self.factory = backplanes.publish_to
        self.factory_args = (mock.Mock(),)

    #---  Tests

    def test_publish_to_should_raise_typeerror_if_no_argument_given(self):
        with self.assert_raises(TypeError):
            ## pylint: disable=E1120
            self.factory()
            ## pylint: enable=E1120

    def test_publish_to_should_return_an_icontainer(self):
        publishing_coroutine = self.make_object()
        self.assert_true(core.IContainer(publishing_coroutine, False))

    def test_publish_to_should_not_emit_normal_messages(self):
        publishing_coroutine = self.make_object()
        message = ('inbox', 'some message')
        result = publishing_coroutine.coroutines[-1].send(message)
        self.assert_is_none(result)

    def test_publish_to_should_forward_ishutdown_messages(self):
        publishing_coroutine = self.make_object()
        shutdown_message = ('control', core.Shutdown())
        result = publishing_coroutine.coroutines[-1].send(shutdown_message)
        self.assert_is_not_none(result)
        self.assert_true(core.IShutdown(result[1], False))


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
