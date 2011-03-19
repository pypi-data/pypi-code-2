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

from pytilities import aop
from pytilities.aop import (
    Aspect, advisor, AOPException
)

unchanged_value = 1
unadvised_value = 3
advised_value = 5

class AdviceTest(unittest.TestCase):

    '''Tests the various advice commands, ...'''

    def detector_advice(self):
        self.detector += 1
        yield aop.proceed

    def detector_advice2(self):
        self.detector2 += 1
        yield aop.proceed

    def advice_suppress_aspect_temporarily(self):
        self.current_advice_count += 1
        o = yield aop.advised_instance
        with (yield aop.suppress_aspect):
            yield aop.return_(o.x)

    def test_suppress_aspect_temporarily(self):
        self.given_detectors_are_reset()

        self.when_apply_advice(get=self.detector_advice)
        self.when_apply_advice(get=self.advice_suppress_aspect_temporarily)
        self.when_apply_advice(get=self.detector_advice2)
        a.reset()
        a.x  # when get x

        self.assertEquals(1, self.detector) # is called on first and second call
        self.assertEquals(1, self.current_advice_count) # is called only on first
        self.assertEquals(2, self.detector2) # is still called

    def advice_proceed(self):
        (self.args, self.kwargs) = yield aop.arguments
        if (len(self.args) > 1):
            self.value = self.args[1]
        (self.name, self.advised) = yield aop.advised_attribute
        self.return_value = yield aop.proceed
        self.advised_instance = yield aop.advised_instance

    def test_proceed_get(self):
        self.when_apply_advice(get=self.advice_proceed)
        self.then_get_returns()
        self.then_arguments_equals((a,), {})
        self.assertIsNotNone(self.advised)
        self.assertEquals('x', self.name)
        self.assertEquals(a, self.advised_instance)

    def test_proceed_set(self):
        self.when_apply_advice(set_=self.advice_proceed)
        self.then_set_proceeds()
        self.then_arguments_equals((a, unadvised_value), {})
        self.assertIsNotNone(self.advised)
        self.assertEquals('x', self.name)
        self.assertEquals(a, self.advised_instance)

    def test_proceed_delete(self):
        self.when_apply_advice(delete=self.advice_proceed)
        self.then_delete_proceeds()
        self.then_arguments_equals((a,), {})
        self.assertIsNotNone(self.advised)
        self.assertEquals('x', self.name)
        self.assertEquals(a, self.advised_instance)

    def test_proceed_call(self):
        self.when_apply_advice(call=self.advice_proceed)
        self.then_call_returns()
        self.then_arguments_equals((a,), {})
        self.assertEquals(af, self.advised)
        self.assertEquals('f', self.name)

    def advice_proceed_with_replaced_arg(self):
        ((s, self.value), kwargs) = yield aop.arguments
        self.return_value = yield aop.proceed(s, advised_value)

    def test_proceed_set_with_replaced_arg(self):
        self.when_apply_advice(set_=self.advice_proceed_with_replaced_arg)
        self.then_set_proceeds(advised_value)

    def advice_return_without_proceed(self):
        yield aop.return_

    def test_return_before_proceed_get(self):
        self.when_apply_advice(get=self.advice_return_without_proceed)
        self.then_get_returns(None)

    def test_return_before_proceed_call(self):
        self.when_apply_advice(call=self.advice_return_without_proceed)
        self.then_call_returns(None)

    def advice_return_with_arg_without_proceed(self):
        yield aop.return_(advised_value)

    def test_return_before_proceed_with_arg_get(self):
        self.when_apply_advice(get=self.advice_return_with_arg_without_proceed)
        self.then_get_returns(advised_value)

    def test_return_before_proceed_with_arg_call(self):
        self.when_apply_advice(call=self.advice_return_with_arg_without_proceed)
        self.then_call_returns(advised_value)

    def advice_return_after_proceed(self):
        self.return_value = yield aop.proceed
        yield aop.return_

    def test_return_after_proceed_get(self):
        self.when_apply_advice(get=self.advice_return_after_proceed)
        self.then_get_returns()

    def test_return_after_proceed_call(self):
        self.when_apply_advice(call=self.advice_return_after_proceed)
        self.then_call_returns()

    def advice_return_with_arg_after_proceed(self):
        self.return_value = yield aop.proceed
        yield aop.return_(advised_value)

    def test_return_with_arg_after_proceed_get(self):
        self.when_apply_advice(get=self.advice_return_with_arg_after_proceed)
        self.then_get_returns(advised_value)

    def test_return_with_arg_after_proceed_call(self):
        self.when_apply_advice(call=self.advice_return_with_arg_after_proceed)
        self.then_call_returns(advised_value)
    
    def advice_fetch_obj(self):
        self.advised_instance = yield aop.advised_instance

    def test_applied_to_instance(self):
        self.when_apply_advice(call=self.advice_fetch_obj)
        self.then_advised_instance_is(a)

    def test_applied_to_class(self):
        self.when_apply_advice(call=self.advice_fetch_obj, to=A)
        self.then_advised_instance_is(a)

    def then_advised_instance_is(self, expected):
        a.f()
        self.assertIs(expected, self.advised_instance)

    def advice_return_values_are_independent_deeper(self):
        (provide_return,), kwargs = yield aop.arguments
        if provide_return: yield aop.return_(1)
        else: yield aop.return_

    def advice_return_values_are_independent_surface(self):
        yield aop.proceed(True)
        yield aop.proceed(False) #Note: this also tests double proceed

    def test_return_values_are_independent(self):
        '''check retvals do not influence each other'''
        self.when_apply_advice(get=self.advice_return_values_are_independent_deeper)
        self.when_apply_advice(get=self.advice_return_values_are_independent_surface)
        a.reset()
        self.assertEquals(None, a.x)

    def test_return_values_are_independent(self):
        '''check retvals do not influence each other'''
        self.when_apply_advice(get=self.advice_return_values_are_independent_deeper)
        self.when_apply_advice(get=self.advice_return_values_are_independent_surface)
        a.reset()
        self.assertEquals(None, a.x)

    def advice_proceed_and_check(self):
        args, kwargs = yield aop.arguments
        self.assertEquals((a, 1, 2), args)
        yield aop.proceed

    def tearDown(self):
        advisor.unapply_all(A)

        if (hasattr(self, 'return_value')):
            del self.return_value #value returned by proceed

        if (hasattr(self, 'value')):
            del self.value #value to which something'd be set

        if (hasattr(self, 'value')):
            del self.args #results from yield arguments

        if (hasattr(self, 'kwargs')):
            del self.kwargs #results from yield arguments

        if (hasattr(self, 'advised')):
            del self.advised

        if (hasattr(self, 'name')):
            del self.name

        if (hasattr(self, 'advised_instance')):
            del self.advised_instance

    def given_detectors_are_reset(self):
        self.detector = 0
        self.detector2 = 0
        self.current_advice_count = 0

    def when_apply_advice(self, get=None, set_=None, delete=None, call=None,
                          to=None):
        if (to is None):
            to = a
        
        AspectGeneric(get, set_, delete, call).apply(to)

    def then_arguments_equals(self, args, kwargs):
        self.assertIsInstance(self.args, tuple)
        self.assertIsInstance(self.kwargs, dict)#should be treated as frozen
        self.assertEquals(args, self.args)
        self.assertEquals(kwargs, self.kwargs)

    def then_get_returns(self, return_value=unchanged_value):
        a.reset()
        self.assertEquals(return_value, a.x)
        if (return_value == unchanged_value):
            self.assertEquals(unchanged_value, self.return_value)

    # value: the value _x ends up having after set to unadvised_value
    def then_set_proceeds(self, value=unadvised_value):
        a.reset()
        a.x = unadvised_value
        self.assertEquals(value, a._x)
        self.assertEquals(unadvised_value, self.value)
        self.assertIs(None, self.return_value)

    def then_delete_proceeds(self):
        a.reset()
        del a.x
        self.assertEquals('deleted', a._x)
        self.assertIs(None, self.return_value)

    def then_call_returns(self, return_value=unchanged_value):
        a.reset()
        self.assertEquals(return_value, a.f())
        if (return_value == unchanged_value):
            self.assertEquals(unchanged_value, self.return_value)

class A(object):

    def reset(self):
        self._x = unchanged_value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        self._x = 'deleted'

    def f(self):
        return unchanged_value

    def g(self, a, b):
        return self, a, b

class AspectGeneric(Aspect):

    def __init__(self, get=None, set_=None, delete=None, call=None):
        Aspect.__init__(self)
        self._advise('x', 'f', 'g', get=get, set_=set_,
                     delete=delete, call=call)


a = A()
af = a.f

