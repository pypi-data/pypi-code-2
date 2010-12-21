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


"""Tests for m4us.core.components."""


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
## pylint: disable=E0611
from zope import interface
## pylint: disable=F0401
from zope.interface import verify
## pylint: enable=E0611, F0401

#---  Project imports
from . import support, test_coroutines
## pylint: disable=E0611
from .. import components, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Support classes

class TheComponent(components.Component):

    interface.classProvides(interfaces.ICoroutineFactory)

    def _main(self):
        return test_coroutines.plain_coroutine()


class CheckComponentTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # ICoroutineTestSupportTrait or CheckStandardMessagesTrait.

    #---  Tests

    def test_factory_should_accept_keyword_arguments(self):
        with self.assert_not_raises(TypeError):
            self.make_object(foo='bar', bat='baz')

    def test_component_should_set_keyword_arguments_as_attributes(self):
        component = self.make_object(foo='bar', bat='baz')
        self.assert_true(hasattr(component, 'foo'))
        self.assert_equal(component.foo, 'bar')
        self.assert_true(hasattr(component, 'bat'))
        self.assert_equal(component.bat, 'baz')

    def test_component_should_initialize_the_contained_coroutine(self):
        component = self.make_object()
        message = self.get_messages()[0]
        response = self.get_responses()[0]
        self.assert_true(hasattr(component, '_coroutine'))
        self.assert_equal(response, component._coroutine.send(message))

    def test_main_should_return_an_icoroutine(self):
        component = self.make_object()
        verify.verifyObject(interfaces.ICoroutine, component._main())


#---  Test classes

class TestRawComponent(support.TestCase):

    # This is a TestCase and not an M4USTestCase because
    # test_object_should_provide_interfaces needs to be disables and it does
    # not work in sub-classes of classes with traits.

    __metaclass__ = strait.include(*support.STANDARD_CLASS_TRAITS)

    #---  Test case settings

    factory = components.Component
    factory_interfaces = (interfaces.ICoroutineFactory,)
    object_interfaces = (interfaces.ICoroutine,)

    #---  Tests

    test_object_should_provide_interfaces = None

    def test_default_main_should_raise_notimplementederror(self):
        with self.assert_raises(NotImplementedError):
            self.make_object()


class TestComponent(support.TestCase):

    __metaclass__ = strait.include(
      test_coroutines.ICoroutineTestSupportTrait,
      CheckComponentTrait,
      *(test_coroutines.BASIC_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = TheComponent

    #---  Throw tests

    def test_throw_should_return_yielded_results(self):
        component = self.make_object()
        exception = IOError()
        message = ('exception', exception)
        # We need this to put the component in the try block.
        component.send('Primer message')
        self.assert_throw_yields_message(component, exception, message)


class TestSampleComponent(support.TestCase):

    __metaclass__ = strait.include(
      CheckComponentTrait,
      *(test_coroutines.STANDARD_ICOROUTINE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = components.SampleComponent


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
