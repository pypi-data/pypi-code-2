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


"""Tests for m4us.core.contatiners."""


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
from . import support, test_components, test_coroutines
## pylint: disable=E0611
from .. import containers, messages, postoffices, exceptions, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Support classes

class IContainerTestSupportTrait(object):

    #---  Support methods

    @support.memoize
    def make_mock_coroutines(self, count):
        return tuple(mock.Mock() for _ in xrange(count))

    def get_coroutines(self):
        return self.make_mock_coroutines(3)

    def get_expected_coroutines(self, container):
        return (container,) + self.get_coroutines()

    def get_expected_sub_coroutines(self, container):
        return self.get_expected_coroutines(container)

    def get_expected_sub_links(self, container):
        return self.get_expected_links(container)

    def get_expected_links(self, container):
        raise NotImplementedError

    def make_container_with_sub_container(self, container):
        raise NotImplementedError


class CheckStandardMessagesTrait(test_coroutines.CheckStandardMessagesTrait):

    #---  Support methods

    def get_responses(self):
        # Overridden.
        response1 = ('_outbox_to_child', 'Hello')
        response2 = ('_outbox_to_child', 'Message 2')
        return (response1, response2)

    def assert_coroutine_shuts_down_on_message(self, container, message):
        # Overridden.
        container.send(('_control_from_child', message))
        with self.assert_raises(StopIteration):
            container.send('This should fail')

    def assert_coroutine_forwards_ishutdown_message(self, container, message):
        # Overridden.
        outbox, message = container.send(('control', message))
        self.assert_equal(outbox, '_signal_to_child')
        self.assert_true(interfaces.IShutdown(message, False))


class CheckIContainerFactoryTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    #---  Test case settings

    factory_interfaces = (interfaces.IContainerFactory,) + \
      test_coroutines.CheckICoroutineFactoryTrait.factory_interfaces

    #---  Tests

    def test_factory_should_accept_multiple_positional_arguments(self):
        if not self.factory_args:
            self.skip_test('No factory arguments provided.')
        with self.assert_not_raises(TypeError):
            self.factory(*self.factory_args, **dict(self.factory_kwargs))


class CheckIContainerTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait,
    # CheckStandardMessagesTrait, IContainerTestSupportTrait,

    #---  Test case settings

    object_interfaces = (interfaces.IContainer,) + \
      test_coroutines.CheckICoroutineTrait.object_interfaces

    #---  Attribute tests

    def test_container_should_set_the_coroutines_attribute(self):
        container = self.make_object()
        expected_coroutines = self.get_expected_coroutines(container)
        for coroutine in expected_coroutines:
            self.assert_in(coroutine, container.coroutines,
              'Expected coroutine "{0}" not found in "coroutines" '
              'attribute.'.format(repr(coroutine)))

    def test_container_should_construct_the_links_attribute(self):
        container = self.make_object()
        expected_links = self.get_expected_links(container)
        for link in expected_links:
            self.assert_in(link, container.links,
              'Expected link "{0}" not found in "links" attribute.'.format(
              repr(link)))

    #---  Main tests

    def test_main_should_forward_inbox_messages_to_child_outbox(self):
        container = self.make_object()
        message = self.get_messages()[0]
        response = container.send(message)
        self.assert_equal(response, ('_outbox_to_child', message[1]))

    def test_main_should_forward_control_messages_to_child_signal(self):
        container = self.make_object()
        message = self.get_messages()[0]
        response = container.send(('control', message[1]))
        self.assert_equal(response, ('_signal_to_child', message[1]))

    def test_main_should_forward_child_inbox_messages_to_outbox(self):
        container = self.make_object()
        message = self.get_messages()[0]
        response = container.send(('_inbox_from_child', message[1]))
        self.assert_equal(response, ('outbox', message[1]))

    def test_main_should_forward_child_control_messages_to_signal(self):
        container = self.make_object()
        message = self.get_messages()[0]
        response = container.send(('_control_from_child', message[1]))
        self.assert_equal(response, ('signal', message[1]))

    def test_main_should_forward_ishutdown_messages_to_child_signal(self):
        container = self.make_object()
        outbox, message = container.send(('control', messages.Shutdown()))
        self.assert_equal(outbox, '_signal_to_child')
        self.assert_true(interfaces.IShutdown(message, False))

    def test_main_should_forward_ishutdowns_from_child_control_to_signal(self):
        container = self.make_object()
        outbox, message = container.send(('_control_from_child',
          messages.Shutdown()))
        self.assert_equal(outbox, 'signal')
        self.assert_true(interfaces.IShutdown(message, False))

    def test_main_should_shutdown_on_ishutdown_from_child_control(self):
        container = self.make_object()
        container.send(('_control_from_child', messages.Shutdown()))
        with self.assert_raises(StopIteration):
            container.send(('inbox', 'This should fail!'))

    #---  Coroutines tests

    def test_coroutines_should_contain_coroutines_from_sub_containers(self):
        container = self.make_object()
        super_container = self.make_container_with_sub_container(container)
        expected_sub_coroutines = self.get_expected_sub_coroutines(container)
        for coroutine in expected_sub_coroutines:
            self.assert_in(coroutine, super_container.coroutines)

    #---  Links tests

    def test_links_should_be_compatible_with_ipostoffice(self):
        container = self.make_object()
        post_office = postoffices.PostOffice()
        with self.assert_not_raises(TypeError):
            with self.assert_not_raises(exceptions.LinkExistsError):
                post_office.link(*container.links)

    def test_links_should_contain_links_from_sub_containers(self):
        container = self.make_object()
        super_container = self.make_container_with_sub_container(container)
        expected_sub_links = self.get_expected_sub_links(container)
        self.assert_equal(expected_sub_links, super_container.links &
          expected_sub_links)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------

STANDARD_ICONTAINER_TRAITS = (
  IContainerTestSupportTrait,
  CheckIContainerFactoryTrait,
  CheckIContainerTrait,
  CheckStandardMessagesTrait,
)


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------

#---  Test classes

class TestGraphline(support.TestCase):

    __metaclass__ = strait.include(
      test_components.CheckComponentTrait,
      *(STANDARD_ICONTAINER_TRAITS +
      test_coroutines.BASIC_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = containers.Graphline
    factory_interfaces = CheckIContainerFactoryTrait.factory_interfaces
    object_interfaces = CheckIContainerTrait.object_interfaces

    #---  Support methods

    def get_expected_links(self, container):
        coroutine1, coroutine2, coroutine3 = self.get_coroutines()
        return set([
          (container, '_outbox_to_child', coroutine1, 'inbox'),
          (container, '_signal_to_child', coroutine1, 'control'),
          (container, '_outbox_to_child', coroutine2, 'inbox'),
          (container, '_signal_to_child', coroutine2, 'control'),
          (coroutine2, 'outbox', coroutine3, 'inbox'),
          (coroutine2, 'signal', coroutine3, 'control'),
          (coroutine1, 'outbox', container, '_inbox_from_child'),
          (coroutine1, 'signal', container, '_control_from_child'),
          (coroutine3, 'outbox', container, '_inbox_from_child'),
          (coroutine3, 'signal', container, '_control_from_child'),
        ])

    def make_container_with_sub_container(self, container):
        return self.factory(
          ('self', 'inbox', container, 'inbox'),
          ('self', 'control', container, 'control'),
        )

    #---  Setup and teardown

    def setup(self):
        coroutine1, coroutine2, coroutine3 = self.get_coroutines()
        self.factory_args = (
          ('self', 'inbox', coroutine1, 'inbox'),
          ('self', 'control', coroutine1, 'control'),
          ('self', 'inbox', coroutine2, 'inbox'),
          ('self', 'control', coroutine2, 'control'),
          (coroutine2, 'outbox', coroutine3, 'inbox'),
          (coroutine2, 'signal', coroutine3, 'control'),
          (coroutine1, 'outbox', 'self', 'outbox'),
          (coroutine1, 'signal', 'self', 'signal'),
          (coroutine3, 'outbox', 'self', 'outbox'),
          (coroutine3, 'signal', 'self', 'signal'),
        )

    #---  Init tests

    def test_init_should_allow_no_links_to_be_given(self):
        with self.assert_not_raises(TypeError):
            self.factory()

    def test_init_should_raise_invalidlinkerror_if_self_inbox_as_inbox(self):
        source = self.get_coroutines()[0]
        with self.assert_raises(exceptions.InvalidLinkError):
            self.factory((source, 'outbox', 'self', 'inbox'))

    def test_init_should_raise_invalidlinkerror_if_self_control_as_inbox(self):
        source = self.get_coroutines()[0]
        with self.assert_raises(exceptions.InvalidLinkError):
            self.factory((source, 'signal', 'self', 'control'))

    def test_init_should_raise_invalidlinkerror_if_self_outbox_as_outbox(self):
        sink = self.get_coroutines()[0]
        with self.assert_raises(exceptions.InvalidLinkError):
            self.factory(('self', 'outbox', sink, 'inbox'))

    def test_init_should_raise_invalidlinkerror_if_self_signal_as_outbox(self):
        sink = self.get_coroutines()[0]
        with self.assert_raises(exceptions.InvalidLinkError):
            self.factory(('self', 'signal', sink, 'control'))

    def test_init_should_allow_custom_mailboxes_on_graphline_instance(self):
        # Note: We are testing both source and sink cases at once.
        graphline = self.factory(('self', 'robin', 'self', 'arthur'))
        self.assert_set_equal(graphline.links, set([(graphline, 'robin',
          graphline, 'arthur')]))


class TestPipeline(support.TestCase):

    __metaclass__ = strait.include(
      test_components.CheckComponentTrait,
      *(STANDARD_ICONTAINER_TRAITS +
      test_coroutines.BASIC_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = containers.Pipeline
    factory_interfaces = CheckIContainerFactoryTrait.factory_interfaces
    object_interfaces = CheckIContainerTrait.object_interfaces

    #---  Support methods

    def get_coroutines(self):
        # Overridden from IContainerTestSupportTrait.
        return self.make_mock_coroutines(5)

    def get_expected_links(self, container):
        coroutines = self.get_coroutines()
        first_child = coroutines[0]
        last_child = coroutines[-1]
        expected_links = set([
          (container, '_outbox_to_child', first_child, 'inbox'),
          (container, '_signal_to_child', first_child, 'control'),
          (last_child, 'outbox', container, '_inbox_from_child'),
          (last_child, 'signal', container, '_control_from_child'),
        ])
        for source, sink in zip(coroutines, coroutines[1:]):
            expected_links.update([
              (source, 'outbox', sink, 'inbox'),
              (source, 'signal', sink, 'control'),
            ])
        return expected_links

    def make_container_with_sub_container(self, container):
        return self.factory(container, mock.Mock())

    #---  Setup and teardown

    def setup(self):
        self.factory_args = self.get_coroutines()

    #---  Init tests

    def test_init_should_raise_typeerror_if_no_coroutines_are_given(self):
        with self.assert_raises(TypeError):
            self.factory()

    def test_init_should_raise_typeerror_if_only_one_coroutine_is_given(self):
        coroutine = self.get_coroutines()[0]
        with self.assert_raises(TypeError):
            self.factory(coroutine)

    def test_init_should_preserve_coroutine_order(self):
        for _ in xrange(10):
            pipeline = self.make_object()
            self.assert_equal(pipeline.coroutines, (pipeline,) +
              self.get_coroutines())


#---Late Module initialization-------------------------------------------------
