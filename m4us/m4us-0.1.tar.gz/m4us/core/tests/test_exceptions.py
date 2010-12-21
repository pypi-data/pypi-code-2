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


"""Tests for m4us.core.exceptions."""


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
from .. import exceptions
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Support classes

class CheckExceptionFactoryTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    def test_factory_should_accept_a_positional_argument(self):
        with self.assert_not_raises(TypeError):
            self.factory('new message', **dict(self.factory_kwargs))

    def test_factory_should_not_require_a_positional_argument(self):
        with self.assert_not_raises(TypeError):
            self.factory(**dict(self.factory_kwargs))

    def test_factory_should_accept_keyword_arguments(self):
        with self.assert_not_raises(TypeError):
            self.factory(foo='bar', bat='baz', **dict(self.factory_kwargs))


class CheckExceptionTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    def test_exception_should_have_a_default_message(self):
        exception = self.factory(**dict(self.factory_kwargs))
        self.assert_true(hasattr(exception, '_message'))
        self.assert_true(isinstance(exception._message, unicode))

    def test_exception_should_store_keyword_arguments_as_attributes(self):
        kwargs = dict(a=1, b=2, c=3)
        exception = self.make_object(**kwargs)
        for attribute, value in kwargs.items():
            self.assert_equal(getattr(exception, attribute), value)

    def test_exception_should_override_message_from_positional_argument(self):
        message = 'Some funky message'
        exception = self.make_object(message)
        self.assert_equal(exception._message, message)

    def test_str_should_return_valid_error_message(self):
        with self.assert_not_raises(KeyError):
            str(self.make_object())

    def test_str_should_format_message_with_attributes(self):
        exception = self.make_object('a={a}, b={b}, c={c}', a=1, b=2, c=3)
        self.assert_equal(str(exception), 'a=1, b=2, c=3')


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------

STANDARD_EXCEPTIONS_TRAITS = (
  CheckExceptionFactoryTrait,
  CheckExceptionTrait,
)


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------

#---  Test classes

class TestM4USException(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.M4USException


#---  Postoffices exceptions

class TestLinkExistsError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.LinkExistsError
    factory_kwargs = ((b'link', 'link'),)


class TestNoLinkError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.NoLinkError
    factory_kwargs = (
      (b'source_outbox', ('source', 'outbox')),
      (b'sink_inbox', ('sink', 'inbox')),
    )


class TestNotASinkError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.NotASinkError
    factory_kwargs = ((b'coroutine', 'coroutine'),)


#---  Schedulers exceptions

class TestDuplicateError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.DuplicateError
    factory_kwargs = ((b'coroutine', 'coroutine'),)


class TestNotAddedError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.NotAddedError
    factory_kwargs = ((b'coroutine', 'coroutine'),)


class TestNeverRunError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.NeverRunError
    factory_kwargs = ((b'coroutine', 'coroutine'),)


#---  Containers exceptions

class TestInvalidLinkError(support.TestCase):

    __metaclass__ = strait.include(
      support.CoreM4USTestSupportTrait,
      *STANDARD_EXCEPTIONS_TRAITS)

    factory = exceptions.InvalidLinkError
    factory_kwargs = (
      (b'source_outbox', ('source', 'outbox')),
      (b'sink_inbox', ('sink', 'inbox')),
    )


#---Late Module initialization-------------------------------------------------
