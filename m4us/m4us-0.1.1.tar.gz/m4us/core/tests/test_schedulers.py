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


"""Tests for m4us.core.schedulers."""


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
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611


#---  Project imports
from . import support
## pylint: disable=E0611
from .. import schedulers, messages, exceptions, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Support classes

class ISchedulerTestSupportTrait(object):

    #---  Support methods

    def make_mock_post_office(self):
        post_office = mock.Mock()
        interface.directlyProvides(post_office, interfaces.IPostOffice)
        # By default, retrieve will signal everything as a producer
        post_office.retrieve.side_effect = exceptions.NotASinkError()
        return post_office

    def make_mock_coroutine(self, lazy=False):
        # By default the mock coroutine will be a producer and so not lazy.
        coroutine = mock.Mock()
        provided_interfaces = [interfaces.ICoroutine]
        if not lazy:
            provided_interfaces.append(interfaces.INotLazy)
        interface.directlyProvides(coroutine, *provided_interfaces)
        # By default, send will not return any messages.
        coroutine.send.return_value = None
        return coroutine

    def make_mock_coroutines(self, count):
        return [self.make_mock_coroutine() for _ in xrange(count)]

    def make_mock_shutting_down_coroutine(self):
        coroutine = self.make_mock_coroutine()
        coroutine.send.return_value = ('signal', messages.Shutdown())
        return coroutine

    def assert_mock_coroutine_sent_ishutdown(self, coroutine):
        call_args = coroutine.send.call_args[0]
        self.assert_equal(call_args[0][0], 'control')
        self.assert_true(interfaces.IShutdown(call_args[0][1], False))


class CheckISchedulerFactoryTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # ISchedulerTestSupportTrait.

    #---  Test case settings

    factory_interfaces = (interfaces.ISchedulerFactory,)

    #--- Factory tests

    def test_factory_should_accept_an_ipostoffice(self):
        post_office = self.make_mock_post_office()
        with self.assert_not_raises(TypeError):
            self.factory(post_office)

    def test_factory_should_raise_typerrror_if_no_post_office_given(self):
        with self.assert_raises(TypeError):
            self.factory()

    def test_factory_should_raise_typerror_if_given_a_non_ipostoffice(self):
        with self.assert_raises(TypeError):
            self.factory(mock.Mock())

    def test_factory_should_accept_argument_add_ignores_duplicates(self):
        with self.assert_not_raises(TypeError):
            self.make_object(add_ignores_duplicates=True)

    def test_factory_should_accept_argument_remove_ignores_missing(self):
        with self.assert_not_raises(TypeError):
            self.make_object(remove_ignores_missing=True)


class CheckISchedulerTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # ISchedulerTestSupportTrait.

    #---  Test case settings

    object_interfaces = (interfaces.IScheduler,)
    test_messages = (('inbox', 'Message 1'), ('inbox', 'Message 2'))

    #---  Add tests

    def test_add_should_accept_a_single_icoroutine_argument(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        with self.assert_not_raises(TypeError):
            scheduler.add(coroutine)

    def test_add_should_accept_multiple_icoroutines_in_one_call(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(4)
        with self.assert_not_raises(TypeError):
            scheduler.add(*coroutines)

    def test_add_should_raise_duplicateerror_if_coroutine_already_added(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        with self.assert_raises(exceptions.DuplicateError):
            scheduler.add(coroutine, coroutine)

    def test_add_should_raise_typeerror_if_given_a_non_icoroutine(self):
        scheduler = self.make_object()
        with self.assert_raises(TypeError):
            scheduler.add(mock.Mock())

    def test_add_should_not_raise_duplicateerror_if_add_is_idempotent(self):
        scheduler = self.make_object(add_ignores_duplicates=True)
        coroutine = self.make_mock_coroutine()
        with self.assert_not_raises(exceptions.DuplicateError):
            scheduler.add(coroutine, coroutine)

    #---  Remove tests

    def test_remove_should_accept_a_single_icoroutine_argument(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        with self.assert_not_raises(TypeError):
            scheduler.remove(coroutine)

    def test_remove_should_accept_multiple_icoroutines_in_one_call(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(4)
        scheduler.add(*coroutines)
        with self.assert_not_raises(Exception):
            scheduler.remove(*coroutines)

    def test_remove_should_close_coroutines(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        scheduler.remove(coroutine)
        self.assert_true(coroutine.close.called)

    def test_remove_should_raise_notaddederror_if_coroutine_not_added(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        with self.assert_raises(exceptions.NotAddedError):
            scheduler.remove(coroutine)

    def test_remove_should_not_raise_notaddederror_if_remove_is_idempotent(
      self):
        scheduler = self.make_object(remove_ignores_missing=True)
        coroutine = self.make_mock_coroutine()
        with self.assert_not_raises(exceptions.NotAddedError):
            scheduler.remove(coroutine)

    #---  Step tests

    def test_step_should_send_messages_to_the_post_office(self):
        post_office = self.make_mock_post_office()
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_coroutine()
        coroutine.send.return_value = ('outbox', 'Message')
        scheduler.add(coroutine)
        scheduler.step()
        expected_result = (coroutine, 'outbox', 'Message')
        self.assert_equal(post_office.post.call_args[0], expected_result)

    def test_step_should_send_all_post_office_messages_to_a_coroutine(self):
        post_office = self.make_mock_post_office()
        post_office.retrieve.side_effect = None
        post_office.retrieve.return_value = self.test_messages
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        scheduler.step()
        self.assert_equal(coroutine.send.call_count, 2)
        for call_args, expected_message in zip(coroutine.send.call_args_list,
          self.test_messages):
            self.assert_equal(call_args[0], (expected_message,))

    def test_step_should_send_none_if_no_messages_and_not_lazy(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        scheduler.step()
        inbox, message = coroutine.send.call_args[0][0]
        self.assert_equal(inbox, 'control')
        self.assert_is_none(message)

    def test_step_should_raise_neverrunerror_if_not_a_sink_and_lazy(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine(lazy=True)
        scheduler.add(coroutine)
        with self.assert_raises(exceptions.NeverRunError):
            scheduler.step()

    def test_step_should_pass_on_nolinkerror_from_post_office_post(self):
        post_office = self.make_mock_post_office()
        post_office.post.side_effect = exceptions.NoLinkError()
        coroutine = self.make_mock_coroutine()
        coroutine.send.return_value = ('outbox', 'Message')
        scheduler = self.factory(post_office)
        scheduler.add(coroutine)
        with self.assert_raises(exceptions.NoLinkError):
            scheduler.step()

    def test_step_should_drop_received_nones(self):
        post_office = self.make_mock_post_office()
        scheduler = self.factory(post_office)
        # Default behaviour of mock coroutine is to return None.
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        for _ in xrange(10):
            scheduler.step()
        self.assert_false(post_office.post.called)

    def test_step_should_drop_unpostable_ishutdown_messages(self):
        post_office = self.make_mock_post_office()
        post_office.post.side_effect = exceptions.NoLinkError()
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_shutting_down_coroutine()
        scheduler.add(coroutine)
        with self.assert_not_raises(exceptions.NoLinkError):
            scheduler.step()

    def test_step_should_flag_a_coroutine_as_shutting_down_on_ishutdown(self):
        # This test is defined as it is part of the IScheduler interface, but
        # the actual requirement is implementation-specific.
        raise NotImplementedError

    def test_step_should_send_ishutdowns_coroutine_until_it_exits(self):
        post_office = self.make_mock_post_office()
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_shutting_down_coroutine()
        scheduler.add(coroutine)
        scheduler.step()
        self.assert_equal(coroutine.send.call_args[0][0], ('control', None))
        coroutine.send.return_value = None
        for _ in xrange(10):
            scheduler.step()
            self.assert_mock_coroutine_sent_ishutdown(coroutine)

    def test_step_should_not_send_post_office_messages_to_shutting_downs(self):
        post_office = self.make_mock_post_office()
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_shutting_down_coroutine()
        scheduler.add(coroutine)
        self.assert_not_in(coroutine, scheduler._shutting_downs)
        scheduler.step()
        self.assert_in(coroutine, scheduler._shutting_downs)
        post_office.retrieve.side_effect = None
        post_office.retrieve.return_value = self.test_messages
        scheduler.step()
        self.assert_mock_coroutine_sent_ishutdown(coroutine)
        # Coroutine should be sent ('control', None) first, then ('control',
        # Shutdown()).  If post office messages had been sent, then
        # call_args_list would be 3 since there are 2 messages in
        # self.test_messages waiting to be delivered.
        self.assert_equal(len(coroutine.send.call_args_list), 2)
        # If post office messages had been sent, then
        # post_office.retrieve.call_count would be 2, once for the ('control',
        # None), messages, and then second for the self.test_messages.
        self.assert_equal(post_office.retrieve.call_count, 1)

    #---  Cycle tests

    def test_cycle_should_run_once_through_all_coroutines(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(5)
        scheduler.add(*coroutines)
        for index, coroutine in enumerate(coroutines):
            self.assert_false(coroutine.send.called,
              'Coroutine {0} already called.'.format(index))
        scheduler.cycle()
        for index, coroutine in enumerate(coroutines):
            self.assert_true(coroutine.send.called,
              'Coroutine {0} not called.'.format(index))

    #---  Run tests

    def test_run_should_support_running_a_fixed_number_of_cycles(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(5)
        scheduler.add(*coroutines)
        for coroutine in coroutines:
            self.assert_false(coroutine.send.called)
        scheduler.run(10)
        for coroutine in coroutines:
            self.assert_equal(coroutine.send.call_count, 10)

    def test_run_should_run_until_all_coroutines_terminate(self):
        # Note: This test kind of relies on scheduler.run() hanging on failure.
        #       As such, it's not a great implementation of the test.  A better
        #       way might be to run scheduler.run() with a timeout of some
        #       kind, but that would probably mean running it in a thread.
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(15)
        for coroutine in coroutines:
            coroutine.send.side_effect = StopIteration
        scheduler.add(*coroutines)
        for coroutine in coroutines:
            self.assert_false(coroutine.send.called)
        scheduler.run()
        for coroutine in coroutines:
            self.assert_true(coroutine.send.called)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------

STANDARD_ISCHEDULER_TRAITS = (
  ISchedulerTestSupportTrait,
  CheckISchedulerFactoryTrait,
  CheckISchedulerTrait,
)


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------

#---  Test classes

class TestScheduler(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_ISCHEDULER_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = schedulers.Scheduler

    #---  Setup and teardown

    def setup(self):
        self.factory_args = (self.make_mock_post_office(),)

    #---  Support methods

    def assert_in_run_queue(self, scheduler, *coroutines):
        for index, coroutine in enumerate(coroutines):
            self.assert_in(coroutine, scheduler._run_queue,
              'Coroutine {0} not in the run queue.'.format(index))

    #---  Add tests

    def test_add_should_add_icoroutines_to_its_run_queue(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        self.assert_in(coroutine, scheduler._run_queue)

    #---  Remove tests

    def test_remove_should_remove_coroutines(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        self.assert_in(coroutine, scheduler._run_queue)
        scheduler.remove(coroutine)
        self.assert_not_in(coroutine, scheduler._run_queue)

    #---  Step tests

    def test_step_should_cycle_the_to_next_coroutine(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(3)
        scheduler.add(*coroutines)
        self.assert_items_equal(coroutines, scheduler._run_queue)
        for _ in xrange(10):
            scheduler.step()
            coroutines.append(coroutines.pop(0))
            self.assert_equal(coroutines, list(scheduler._run_queue))

    def test_step_should_remove_terminated_coroutines_from_the_run_queue(self):
        coroutine = self.make_mock_coroutine()
        coroutine.send.side_effect = StopIteration
        scheduler = self.make_object()
        scheduler.add(coroutine)
        self.assert_in(coroutine, scheduler._run_queue)
        scheduler.step()
        self.assert_not_in(coroutine, scheduler._run_queue)

    def test_step_should_flag_a_coroutine_as_shutting_down_on_ishutdown(self):
        # Overridden method.
        post_office = self.make_mock_post_office()
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_shutting_down_coroutine()
        scheduler.add(coroutine)
        scheduler.step()
        self.assert_in(coroutine, scheduler._shutting_downs)

    def test_step_should_remove_exited_coroutines_from_shutting_downs(self):
        post_office = self.make_mock_post_office()
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_shutting_down_coroutine()
        scheduler.add(coroutine)
        scheduler.step()
        self.assert_in(coroutine, scheduler._shutting_downs)
        coroutine.send.side_effect = StopIteration
        scheduler.step()
        self.assert_not_in(coroutine, scheduler._shutting_downs)
        self.assert_not_in(coroutine, scheduler._run_queue)

    #---  _Get_inbox_messages tests

    def test_get_inbox_messages_should_return_all_messages_for_coroutine(self):
        post_office = self.make_mock_post_office()
        post_office.retrieve.side_effect = None
        post_office.retrieve.return_value = self.test_messages
        scheduler = self.factory(post_office)
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        messages_ = scheduler._get_inbox_messages(coroutine)
        self.assert_equal(len(messages_), 2)
        for message, expected_message in zip(messages_, self.test_messages):
            self.assert_equal(message, expected_message)

    def test_get_inbox_messages_should_return_none_if_no_msg_and_no_lazy(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        messages_ = scheduler._get_inbox_messages(coroutine)
        self.assert_equal(len(messages_), 1)
        inbox, message = messages_[0]
        self.assert_equal(inbox, 'control')
        self.assert_is_none(message)

    def test_get_inbox_messages_should_raise_neverrunerror_if_notasink(self):
        # But only if coroutine is also lazy
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine(lazy=True)
        scheduler.add(coroutine)
        with self.assert_raises(exceptions.NeverRunError):
            scheduler._get_inbox_messages(coroutine)

    def test_get_inbox_messages_should_return_ishutdown_if_shutting_down(self):
        scheduler = self.make_object()
        coroutine = self.make_mock_coroutine()
        scheduler.add(coroutine)
        scheduler._shutting_downs.add(coroutine)
        messages_ = scheduler._get_inbox_messages(coroutine)
        self.assert_equal(len(messages_), 1)
        inbox, message = messages_[0]
        self.assert_equal(inbox, 'control')
        self.assert_true(interfaces.IShutdown(message, False))

    #---  Cycle tests

    def test_cycle_should_handle_a_shrinking_run_queue(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(7)
        for coroutine in coroutines:
            coroutine.send.side_effect = StopIteration
        scheduler.add(*coroutines)
        self.assert_in_run_queue(scheduler, *coroutines)
        scheduler.cycle()
        self.assert_equal(len(scheduler._run_queue), 0)

    #---  Run tests

    def test_run_should_run_until_run_queue_is_empty(self):
        scheduler = self.make_object()
        coroutines = self.make_mock_coroutines(15)
        for coroutine in coroutines:
            coroutine.send.side_effect = StopIteration
        scheduler.add(*coroutines)
        self.assert_in_run_queue(scheduler, *coroutines)
        scheduler.run()
        self.assert_equal(len(scheduler._run_queue), 0)


#---Late Module initialization-------------------------------------------------
