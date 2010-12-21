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


"""Tests for m4us.core.coroutines."""


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
from .. import coroutines, messages, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

#---  Support coroutines

def plain_coroutine():
    message = (yield)
    while True:
        try:
            message = (yield message)
        ## pylint: disable=W0703
        except Exception as error:
            ## pylint: enable=W0703
            message = ('exception', error)


@coroutines.coroutine()
def decorated_coroutine():
    return plain_coroutine()


@coroutines.coroutine(lazy=False)
def non_lazy_coroutine():
    return plain_coroutine()


@coroutines.coroutine()
def coroutine_with_parameters(first, second, third=None, fourth=None):
    yield
    yield 'outbox', dict(first=first, second=second, third=third,
      fourth=fourth)


#---Classes--------------------------------------------------------------------

#---  Support classes

class ICoroutineTestSupportTrait(object):

    #---  Support methods

    def get_messages(self):
        return ('Hello', 'Message 2')

    def get_responses(self):
        return self.get_messages()

    def assert_throw_yields_message(self, coroutine, exception, message):
        result = coroutine.throw(exception)
        self.assert_equal(result, message)


class INotLazyTestSupportTrait(object):

    def assert_is_lazy(self, coroutine):
        self.assert_false(interfaces.INotLazy.providedBy(coroutine))
        self.assert_false(interfaces.INotLazy(coroutine, False))

    def assert_not_lazy(self, coroutine):
        self.assert_true(interfaces.INotLazy(coroutine, False))

    def assert_adapts_to_inotlazy(self, coroutine):
        self.assert_false(interfaces.INotLazy.providedBy(coroutine))
        self.assert_not_lazy(coroutine)


class CheckICoroutineFactoryTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    #---  Test case settings

    factory_interfaces = (interfaces.ICoroutineFactory,)


class CheckICoroutineTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # ICoroutineTestSupportTrait.

    #---  Test case settings

    object_interfaces = (interfaces.ICoroutine,)

    #---  Send tests

    def test_icoroutine_should_send_and_receive_messages(self):
        coroutine = self.make_object()
        messages_ = self.get_messages()
        responses = self.get_responses()
        for message, response in zip(messages_, responses):
            self.assert_equal(coroutine.send(message), response)

    def test_send_should_raise_stopiteration_if_coroutine_is_closed(self):
        coroutine = self.make_object()
        coroutine.close()
        with self.assert_raises(StopIteration):
            coroutine.send('This should fail')

    #---  Throw tests

    def test_throw_should_raise_unhandled_thrown_exception(self):
        coroutine = self.make_object()
        with self.assert_raises(IOError):
            coroutine.throw(IOError())

    def test_throw_should_raise_given_exception_if_coroutine_is_closed(self):
        coroutine = self.make_object()
        coroutine.close()
        with self.assert_raises(ValueError):
            coroutine.throw(ValueError())

    #---  Close tests

    def test_repeated_calls_to_close_should_have_no_effect(self):
        coroutine = self.make_object()
        coroutine.close()
        with self.assert_not_raises(Exception):
            for _ in xrange(5):
                coroutine.close()


class CheckStandardMessagesTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    #---  Support methods

    def assert_coroutine_shuts_down_on_message(self, coroutine, message):
        coroutine.send(('control', message))
        with self.assert_raises(StopIteration):
            coroutine.send('This should fail')

    def assert_coroutine_forwards_ishutdown_message(self, coroutine, message):
        outbox, message = coroutine.send(('control', message))
        self.assert_equal(outbox, 'signal')
        self.assert_true(interfaces.IShutdown(message, False))

    def get_messages(self):
        message1 = ('inbox', 'Hello')
        message2 = ('inbox', 'Message 2')
        return (message1, message2)

    def get_responses(self):
        response1 = ('outbox', 'Hello')
        response2 = ('outbox', 'Message 2')
        return (response1, response2)

    #---  IShutdown tests

    def test_icoroutine_should_shutdown_on_shutdown_message(self):
        coroutine = self.make_object()
        self.assert_coroutine_shuts_down_on_message(coroutine,
          messages.Shutdown())

    def test_icoroutine_should_forward_the_shutdown_message(self):
        coroutine = self.make_object()
        self.assert_coroutine_forwards_ishutdown_message(coroutine,
          messages.Shutdown())

    #---  IProducerFinished tests

    def test_icoroutine_should_shutdown_on_producerfinished_message(self):
        coroutine = self.make_object()
        self.assert_coroutine_shuts_down_on_message(coroutine,
          messages.ProducerFinished())

    def test_icoroutine_should_forward_the_producerfinished_message(self):
        coroutine = self.make_object()
        self.assert_coroutine_forwards_ishutdown_message(coroutine,
          messages.ProducerFinished())


class CheckUninitializedCoroutineTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # ICoroutineTestSupportTrait or CheckStandardMessagesTrait.

    def test_coroutine_should_raise_typeerror_if_first_send_is_not_none(self):
        coroutine = self.make_object()
        message = self.get_messages()[0]
        with self.assert_raises(TypeError):
            coroutine.send(message)


class CheckInitializedCoroutineTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # ICoroutineTestSupportTrait or CheckStandardMessagesTrait.

    def test_coroutine_should_not_raise_typeerror_if_first_send_not_none(self):
        coroutine = self.make_object()
        message = self.get_messages()[0]
        with self.assert_not_raises(TypeError):
            coroutine.send(message)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------

BASIC_ICOROUTINE_TRAITS = (
  CheckICoroutineFactoryTrait,
  CheckICoroutineTrait,
  CheckInitializedCoroutineTrait,
)
STANDARD_ICOROUTINE_TRAITS = BASIC_ICOROUTINE_TRAITS + (
  CheckStandardMessagesTrait,
)

#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------

#---  Test classes

class TestRawCoroutine(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      ICoroutineTestSupportTrait,
      CheckUninitializedCoroutineTrait,
    )

    #--- Setup and teardown

    def setup(self):
        self.factory = plain_coroutine


class TestCoroutine(support.TestCase):

    __metaclass__ = strait.include(
      ICoroutineTestSupportTrait,
      *(BASIC_ICOROUTINE_TRAITS +
      support.STANDARD_FUNCTION_TRAITS))

    #---  Setup and teardown

    def setup(self):
        self.factory = decorated_coroutine

    #---  Tests

    def test_throw_should_return_yielded_results(self):
        coroutine = self.make_object()
        primer_message = self.get_messages()[0]
        exception = IOError()
        message = ('exception', exception)
        coroutine.send(primer_message)  # Put the coroutine in the while loop.
        self.assert_throw_yields_message(coroutine, exception, message)


class TestSampleCoroutine(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_ICOROUTINE_TRAITS +
      support.STANDARD_FUNCTION_TRAITS))

    #---  Setup and teardown

    def setup(self):
        self.factory = coroutines.sample_coroutine


class TestCoroutineDecorator(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      ICoroutineTestSupportTrait,
      INotLazyTestSupportTrait,
    )

    # Note: We cannot use mock.Mock for mock coroutines as coroutines.coroutine
    # can only be applied to functions and unbound methods.

    #---  Setup and teardown

    def setup(self):
        self.factory = decorated_coroutine
        self.make_coroutine_with_parameters = coroutine_with_parameters
        self.make_non_lazy_coroutine = non_lazy_coroutine

    #---  Tests

    def test_decorator_should_initialize_the_coroutine_when_called(self):
        coroutine = self.make_object()
        with self.assert_not_raises(TypeError):
            coroutine.send('Non-None value')

    def test_decorator_should_pass_all_args_to_the_decorated_function(self):
        coroutine = self.make_coroutine_with_parameters(9, 8, fourth=7,
          third=6)
        message = self.get_messages()[0]
        _, kwargs = coroutine.send(message)
        self.assert_equal(dict(first=9, second=8, third=6, fourth=7), kwargs)

    def test_decorator_should_support_setting_coroutine_laziness(self):
        lazy_coroutine = self.make_object()
        non_lazy_coroutine_ = self.make_non_lazy_coroutine()
        self.assert_is_lazy(lazy_coroutine)
        self.assert_not_lazy(non_lazy_coroutine_)


class TestNullSink(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_ICOROUTINE_TRAITS +
      support.STANDARD_FUNCTION_TRAITS))

    #---  Setup and teardown

    def setup(self):
        self.factory = coroutines.null_sink

    #---  Tests

    # Overridden and removed because it does not apply.
    test_icoroutine_should_send_and_receive_messages = None

    def test_null_sink_should_recieve_but_not_emit_non_shutdown_messages(self):
        coroutine = self.make_object()
        message = self.get_messages()[0]
        result = coroutine.send(message)
        self.assert_is(result, None)


class TestNonLazyCoroutineRegistry(support.TestCase):

    __metaclass__ = strait.include(support.CoreM4USTestSupportTrait)

    #---  Test case settings

    factory = coroutines._NonLazyCoroutineRegistry

    #---  Support methods

    def register_and_check_registration(self, registry, coroutine):
        self.assert_not_in(id(coroutine), registry._non_lazy_coroutines)
        registry.register(coroutine)
        self.assert_in(id(coroutine), registry._non_lazy_coroutines)

    #---  Setup and teardown

    def setup(self):
        self.coroutine_factory = decorated_coroutine

    def teardown(self):
        self.factory._non_lazy_coroutines.clear()

    #--- Instance tests

    def test_multiple_instances_should_share_the_same_data(self):
        registry = self.make_object()
        registry2 = self.make_object()
        coroutine = self.coroutine_factory()
        self.assert_false(registry2.is_non_lazy(coroutine))
        self.register_and_check_registration(registry, coroutine)
        self.assert_true(registry2.is_non_lazy(coroutine))

    #---  Register tests

    def test_register_should_register_a_coroutine_as_non_lazy(self):
        registry = self.make_object()
        coroutine = self.coroutine_factory()
        self.register_and_check_registration(registry, coroutine)

    def test_register_should_be_idempotent(self):
        registry = self.make_object()
        coroutine = self.coroutine_factory()
        self.register_and_check_registration(registry, coroutine)
        with self.assert_not_raises(Exception):
            registry.register(coroutine)

    #--- Is_non_lazy tests

    def test_is_non_lazy_should_return_false_if_coroutine_is_lazy(self):
        registry = self.make_object()
        coroutine = self.coroutine_factory()
        self.assert_false(registry.is_non_lazy(coroutine))

    def test_is_non_lazy_should_return_true_if_coroutine_is_non_lazy(self):
        registry = self.make_object()
        coroutine = self.coroutine_factory()
        self.assert_false(registry.is_non_lazy(coroutine))
        registry.register(coroutine)
        self.assert_true(registry.is_non_lazy(coroutine))


class TestICoroutineToINotLazyAdapter(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      INotLazyTestSupportTrait,
    )

    #---  Setup and teardown

    def setup(self):
        self.factory = coroutines._icoroutine_to_inotlazy_adapter
        self.registry_factory = coroutines._NonLazyCoroutineRegistry
        self.coroutine_factory = decorated_coroutine

    #---  Tests

    def test_adapter_should_return_none_if_coroutine_is_lazy(self):
        coroutine = self.coroutine_factory()
        result = self.make_object(coroutine)
        self.assert_is(result, None)

    def test_adapter_should_return_coroutine_if_coroutine_is_not_lazy(self):
        coroutine = self.coroutine_factory()
        registry = self.registry_factory()
        registry.register(coroutine)
        result = self.make_object(coroutine)
        self.assert_is(result, coroutine)

    def test_lazy_coroutine_should_not_provide_or_adapt_to_inotlazy(self):
        coroutine = self.coroutine_factory()
        self.assert_is_lazy(coroutine)

    def test_non_lazy_coroutine_should_adapt_to_inotlazy(self):
        coroutine = self.coroutine_factory()
        registry = self.registry_factory()
        registry.register(coroutine)
        self.assert_adapts_to_inotlazy(coroutine)


#---Late Module initialization-------------------------------------------------
