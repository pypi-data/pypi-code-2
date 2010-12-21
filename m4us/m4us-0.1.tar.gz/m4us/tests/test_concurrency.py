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


"""Tests for m4us.concurrency."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import time
import Queue

#---  Third-party imports
import mock
import strait

#---  Project imports
from ..core import api as core
## pylint: disable=E0611
from .. import concurrency, interfaces
## pylint: enable=E0611
from ..core.tests import test_coroutines, support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#--- Support classes

class ConcurrencyTestSupportTrait(object):

    @support.memoize
    def get_coroutine(self):
        return test_coroutines.decorated_coroutine()


#---  Test classes

class TestCoroutineThread(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      ConcurrencyTestSupportTrait,
    )

    #---  Test case settings

    factory = concurrency._CoroutineThread

    #---  Support methods

    def  get_messages(self):
        return (
          ('inbox', 'message 1'),
          ('inbox', 'message 2'),
        )

    @support.memoize
    def get_queues(self):
        in_queue = Queue.Queue()
        out_queue = Queue.Queue()
        return in_queue, out_queue

    def make_shutdown_message(self):
        return ('_thread_control', core.Shutdown())

    #---  Setup and teardown

    def setup(self):
        self.factory_args = (self.get_coroutine(),) + self.get_queues()

    #---  Init tests

    def test_init_should_require_a_coroutine(self):
        with self.assert_raises(TypeError):
            self.factory()

    def test_init_should_require_an_input_queue(self):
        coroutine = self.get_coroutine()
        with self.assert_raises(TypeError):
            self.factory(coroutine)

    def test_init_should_require_an_output_queue(self):
        coroutine = self.get_coroutine()
        in_queue = self.get_queues()[0]
        with self.assert_raises(TypeError):
            self.factory(coroutine, in_queue)

    #---  Run tests

    def test_run_should_shutdown_on_ishutdown_message(self):
        thread = self.make_object()
        in_queue = self.get_queues()[0]
        shutdown_message = self.make_shutdown_message()
        self.assert_false(thread.is_alive())
        thread.start()
        self.assert_true(thread.is_alive())
        in_queue.put(shutdown_message)
        thread.join()
        self.assert_false(thread.is_alive())

    def test_run_should_send_and_receive_queued_coroutine_messages(self):
        thread = self.make_object()
        in_queue, out_queue = self.get_queues()
        messages = self.get_messages()
        shutdown_message = self.make_shutdown_message()
        thread.start()
        for message in messages:
            in_queue.put(message)
        in_queue.put(shutdown_message)
        thread.join()
        for message in messages:
            self.assert_equal(out_queue.get_nowait(), message)

    def test_run_should_throw_queued_exceptions_to_the_coroutine(self):
        exception = IOError()
        thread = self.make_object()
        in_queue, out_queue = self.get_queues()
        primer_message = self.get_messages()[0]
        shutdown_message = self.make_shutdown_message()
        thread.start()
        in_queue.put(primer_message)
        in_queue.put(('_thread_exception', exception))
        in_queue.put(shutdown_message)
        thread.join()
        out_queue.get_nowait()  # Get the response to the primer message.
        self.assert_equal(out_queue.get_nowait(), ('exception', exception))

    def test_run_should_close_coroutine_on_shutdown(self):
        thread = self.make_object()
        coroutine = self.get_coroutine()
        in_queue = self.get_queues()[0]
        messages = self.get_messages()
        shutdown_message = self.make_shutdown_message()
        thread.start()
        for message in messages:
            in_queue.put(message)
        in_queue.put(shutdown_message)
        thread.join()
        with self.assert_raises(StopIteration):
            coroutine.send(messages[0])

    def test_run_should_shutdown_if_coroutine_shuts_down(self):
        in_queue, out_queue = self.get_queues()
        # This relies on the fact that coroutine_with_parameters dies after
        # it's second message.
        thread = self.factory(test_coroutines.coroutine_with_parameters(1, 2),
          in_queue, out_queue)
        messages = self.get_messages()
        thread.start()
        for message in messages:  # Second message triggers StopIteration
            in_queue.put(message)
        thread.join()
        self.assert_false(thread.is_alive())


class TestThreadedCoroutine(support.TestCase):

    __metaclass__ = strait.include(
      ConcurrencyTestSupportTrait,
      test_coroutines.ICoroutineTestSupportTrait,
      *(test_coroutines.BASIC_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    _make_object = support.CoreM4USTestSupportTrait.make_object.__func__

    #--- Test case settings

    factory = concurrency.ThreadedCoroutine
    object_interfaces = (interfaces.IThreadedCoroutine, core.INotLazy) + \
      test_coroutines.CheckICoroutineTrait.object_interfaces

    #---  Support methods

    def get_messages(self):
        return (
          ('inbox', 'Hello'),
          ('inbox', 'Message 2'),
        )

    def wait_for_message(self, coroutine, first_result):
        outbox_message = first_result
        for _ in xrange(100):
            if outbox_message is not None:
                break
            time.sleep(0.1)
            outbox_message = coroutine.send(('control', None))
        else:
            self.fail('Timed out waiting for coroutine to return a message.')
        return outbox_message

    def make_object(self, *args, **kwargs):
        # Overridden from support.CoreM4USTestSupportTrait.make_object.
        coroutine = self._make_object(*args, **kwargs)
        self._threaded_coroutines.append(coroutine)
        return coroutine

    #---  Setup and teardown

    def setup(self):
        self.factory_args = (self.get_coroutine(),)
        self._threaded_coroutines = []

    def teardown(self):
        for coroutine in self._threaded_coroutines:
            try:
                coroutine.close()
            except RuntimeError:
                pass
        del self._threaded_coroutines

    #---  Init tests

    def test_init_should_require_a_coroutine_as_an_argument(self):
        with self.assert_raises(TypeError):
            self.factory()

    def test_init_should_require_an_icoroutine_as_its_first_argument(self):
        with self.assert_raises(TypeError):
            self.factory(mock.Mock())

    def test_init_should_allow_limiting_the_input_queue_size(self):
        coroutine = self.make_object(max_in_size=4)
        self.assert_equal(coroutine._in_queue.maxsize, 4)

    def test_init_should_allow_limiting_the_output_queue_size(self):
        coroutine = self.make_object(max_out_size=17)
        self.assert_equal(coroutine._out_queue.maxsize, 17)

    def test_init_should_start_the_thread_by_default(self):
        coroutine = self.make_object()
        self.assert_true(coroutine._thread.is_alive())

    def test_init_should_allow_the_thread_to_not_be_started_by_default(self):
        coroutine = self.make_object(start=False)
        self.assert_false(coroutine._thread.is_alive())

    #---  Start tests

    def test_start_should_start_the_thread(self):
        coroutine = self.make_object(start=False)
        self.assert_false(coroutine._thread.is_alive())
        coroutine.start()
        self.assert_true(coroutine._thread.is_alive())

    def test_start_should_raise_runtimeerror_if_thread_already_started(self):
        coroutine = self.make_object()
        with self.assert_raises(RuntimeError):
            coroutine.start()

    #---  Send tests

    def test_icoroutine_should_send_and_receive_messages(self):
        # Overridden method from test_coroutines.CheckICoroutineTrait.
        coroutine = self.make_object()
        messages = self.get_messages()
        responses = self.get_responses()
        for message, response in zip(messages, responses):
            outbox_message = coroutine.send(message)
            outbox_message = self.wait_for_message(coroutine, outbox_message)
            self.assert_equal(outbox_message, response)

    def test_send_should_return_none_if_no_message_in_output_queue(self):
        coroutine = self.make_object(start=False)
        message = self.get_messages()[0]
        self.assert_equal(coroutine.send(message), None)

    def test_send_should_swallow_none_messages_to_lazy_coroutines(self):
        coroutine = self.make_object()
        self.assert_equal(coroutine.send(('control', None)), None)

    #---  Throw tests

    def test_throw_should_raise_unhandled_thrown_exception(self):
        # Overridden method test_coroutines.CheckICoroutineTrait.
        coroutine = self.make_object()
        with self.assert_raises(IOError):
            coroutine.throw(IOError())
            for _ in xrange(100):
                time.sleep(0.1)
                coroutine.send(('control', None))

    def test_throw_should_return_yielded_results(self):
        exception = IOError()
        coroutine = self.make_object()
        primer_message = self.get_messages()[0]
        # We have to prime decorated_coroutine to get it in the while loop with
        # the exception handling.
        self.wait_for_message(coroutine, coroutine.send(primer_message))
        outbox_message = coroutine.throw(exception)
        outbox_message = self.wait_for_message(coroutine, outbox_message)
        self.assert_equal(outbox_message[1], exception)

    def test_throw_should_return_none_if_no_message_in_output_queue(self):
        coroutine = self.make_object(start=False)
        self.assert_equal(coroutine.throw(IOError()), None)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
