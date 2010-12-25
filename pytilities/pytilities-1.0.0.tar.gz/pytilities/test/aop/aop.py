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
import pdb

from pytilities.aop import (
    proceed, return_, arguments, advised,
    advisor, Aspect, AOPMeta
)

def make_A():
    class A(object, metaclass=AOPMeta):
        def __init__(self):
            self.__x = 5

        @property
        def x(self):
            return self.__x

        @x.setter
        def x(self, value):
            self.__x = value

        def f(self, a, b):
            return self, a + b, a - b

        @classmethod
        def g(cls, a):
            return cls, a

        @staticmethod
        def h(a):
            return a

        def k(self, a):
            return a

    return A


class Aspect1(Aspect):
    '''Advice most attribs, but do nothing but proceed'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('x', 'f', 'g', 'h',
            get = self.advice_proceed, set_ = self.advice_proceed,
            delete = self.advice_proceed, call = self.advice_proceed)

    def advice_proceed(self):
        yield proceed

aspect1 = Aspect1()

class Aspect2(Aspect):
    '''Advice all attribs with a noop, using the special * attrib'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('*',
            get = self.advice_proceed, set_ = self.advice_proceed,
            delete = self.advice_proceed, call = self.advice_proceed)

    def advice_proceed(self):
        self.__hit = True
        yield proceed

    def was_hit(self):
        hit = self.__hit
        self.__hit = False
        return hit

aspect2 = Aspect2()

class Aspect3(Aspect):
    '''Advice most attribs, but do nothing but proceed with a changed arg'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('h', call = self.advice)

    def advice(self):
        h = yield advised
        yield return_(h(7))

aspect3 = Aspect3()

class Aspect4(Aspect):
    '''Advice a non-existing attribute to return 3'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('z',
            get = self.advice)

    def advice(self):
        yield return_(3)

aspect4 = Aspect4()

def h_num(num):
    def h():
        yield return_(num)
    return h

class Aspect5C1(Aspect):
    '''First class advice of test 5'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('x', get=self.x_get, set_=self.x_set)
        self._advise('f', call=self.f)
        self._advise('h', 'k', call=h_num(1))

    def x_get(self):
        ret = yield proceed
        yield return_(ret * 2)

    def x_set(self):
        while True:
            args, kwargs = yield arguments
            args = list(args)
            args[1] += 1
            yield proceed(*args)
            yield return_

    def f(self):
        args, kwargs = yield arguments
        yield proceed(args[0], args[2], args[1])

aspect5C1 = Aspect5C1()

class Aspect5I1(Aspect):
    '''First instance advice of test 5'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('x', get=self.x_get)
        self._advise('f', call=self.f)
        self._advise('h', 'k', call=h_num(3))

    def x_get(self):
        ret = yield proceed
        yield return_(ret + 1)

    def f(self):
        args, kwargs = yield arguments
        yield proceed(*args)
        ret = yield proceed(*args) # intentionally proceed twice
        yield return_(ret[:-1] + (4,))

aspect5I1 = Aspect5I1()

class Aspect5C2(Aspect):
    '''Second class advice of test 5'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('x', get=self.x_get, set_=self.x_set)
        self._advise('f', call=self.f)
        self._advise('h', 'k', call=h_num(2))

    def x_get(self):
        ret = yield proceed
        yield return_(ret - 2)

    def x_set(self):
        ((self, a,),kw) = yield arguments
        yield proceed(self, a * 2)
        yield return_

    def f(self):
        args, kw = yield arguments
        yield proceed
        yield proceed(args[0], 10, 10) # intentionally proceed twice

aspect5C2 = Aspect5C2()

class Aspect5I2(Aspect):
    '''Second instance advice of test 5'''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('x', get=self.x_get, set_=self.x_set)
        self._advise('f', call=self.f)
        self._advise('h', 'k', call=h_num(4))

    def x_get(self):
        ret = yield proceed
        yield return_(ret * 4)

    def x_set(self):
        args, kwargs = yield arguments
        yield proceed(args[0], args[0].x)
        yield return_

    def f(self):
        yield return_(5)

aspect5I2 = Aspect5I2()

class Aspect6(Aspect):
    '''instance advice of test 6'''

    def __init__(self):
        Aspect.__init__(self)
        # advise to return something callable on get (it needs to be so it can
        # be wrapped). Then advise the call to just ret 2.
        self._advise('__len__', get=self.get_, call=self.len_)

    def get_(self):
        yield return_(lambda: None)

    def len_(self):
        yield return_(2)

aspect6 = Aspect6()

class ClassTest(unittest.TestCase):
    '''Test class and instance advice'''

    def setUp(self):
        self.A = make_A()

    def test_1_single_class(self):
        '''test giving a noop advice to all instances of class'''
        # Makes sure nothing serious is broken:
        # - instance methods, class methods, static methods, properties
        # - class access, instance access
        # 
        # No instance advice testing though
        aspect1.apply(self.A)

        a = self.A()
        self.assertEquals(a.x, 5) # descriptor get
        a.x = 3
        self.assertEquals(a.x, 3) # descriptor set
        self.assertEquals(a.f(5, 2), (a, 7, 3)) # bound call
        self.assertEquals(self.A.f(a, 5, 2), (a, 7, 3)) # unbound call
        self.assertEquals(a.g(2), (self.A, 2)) # class bound call
        self.assertEquals(self.A.g(2), (self.A, 2)) # class bound call
        self.assertEquals(a.h(2), 2) # static call
        self.assertEquals(self.A.h(2), 2) # static call

    def test_2_star_advice(self):
        '''test giving proceed advice to everything, using *'''
        # test everything still works, and advice is called every time
        aspect2.apply(self.A)

        a = self.A()
        self.assertEquals(a.x, 5) # descriptor get
        self.assert_(aspect2.was_hit())
        a.x = 3
        self.assert_(aspect2.was_hit())
        self.assertEquals(a.x, 3) # descriptor set
        self.assert_(aspect2.was_hit())
        self.assertEquals(a.f(5, 2), (a, 7, 3)) # bound call
        self.assert_(aspect2.was_hit())
        self.assertEquals(self.A.f(a, 5, 2), (a, 7, 3)) # unbound call
        self.assert_(aspect2.was_hit())
        self.assertEquals(a.g(2), (self.A, 2)) # class bound call
        self.assert_(aspect2.was_hit())
        self.assertEquals(self.A.g(2), (self.A, 2)) # class bound call
        self.assert_(aspect2.was_hit())
        self.assertEquals(a.h(2), 2) # static call
        self.assert_(aspect2.was_hit())
        self.assertEquals(self.A.h(2), 2) # static call
        self.assert_(aspect2.was_hit())

    def test_3_advised(self):
        '''tests yielding advised'''
        aspect3.apply(self.A)
        self.assertEquals(self.A.h(5), 7)

    def test_4_non_existent(self):
        '''test giving advice to an attribute that's not there'''
        # this is getting slight laughable
        # once upon a time there was a nothing, we advised the nothing, and
        # the nothing got more clever. Clever as the nothing was, it would only
        # work on the advised instance that carries the nothing, ...

        aspect4.apply(self.A)

        a = self.A()
        self.assertEquals(a.z, 3) 

    def test_5_multiple_advice(self):
        '''
        test multiple advice using all yield commands, on class and instance
        '''
        # 2 advices on class level and 2 on instance level + another on a
        # different instance
        # tested on a callable and property
        # Also helps see the order of advice proceeding is correct
        #
        # Applied advice:
        #     get   set   f             h   k
        # C1: *2    +1    a, b = b, a   1   1
        # C2: -2    *2    a=b=10        2   2
        # I1: +1          r=a,4         3   3 #note: h is static method
        # I2: *4    val=x r=5           4   4 # so inst advice does not affect it

        # create 2 instances
        a = self.A()
        a2 = self.A()
        
        # first class advice
        aspect5C1.apply(self.A)

        # check everything still works
        self.assertEquals(a.x, 10) # x get?
        a.x = 3
        self.assertEquals(a.x, 8) # x set?
        a.x = 4
        self.assertEquals(a.x, 10) # x set still worked?
        self.assertEquals(a.f(3, 4), (a, 7, 1)) # f works?
        self.assertEquals(a.h(0), 1)
        self.assertEquals(a.k(0), 1) # test order of execution

        self.assertEquals(a2.x, 10) # x get?
        a2.x = 3
        self.assertEquals(a2.x, 8) # x set?
        a2.x = 4
        self.assertEquals(a2.x, 10) # x set still worked?
        self.assertEquals(a2.f(3, 4), (a2, 7, 1)) # f works?
        self.assertEquals(a2.h(0), 1)
        self.assertEquals(a2.k(0), 1) # test order of execution

        # first instance advice
        aspect5I1.apply(a)

        # check everything still works
        self.assertEquals(a.x, 11)
        a.x = 3
        self.assertEquals(a.x, 9)
        a.x = 4
        self.assertEquals(a.x, 11)
        self.assertEquals(a.f(3, 4), (a, 7, 4))
        self.assertEquals(a.h(0), 3)
        self.assertEquals(a.k(0), 3) # test order of execution

        # other instance is unaffected by a's instance advice?
        self.assertEquals(a2.x, 10) # x get?
        a2.x = 3
        self.assertEquals(a2.x, 8) # x set?
        a2.x = 4
        self.assertEquals(a2.x, 10) # x set still worked?
        self.assertEquals(a2.f(3, 4), (a2, 7, 1)) # f works?
        self.assertEquals(a2.h(0), 1)
        self.assertEquals(a2.k(0), 1) # test order of execution

        # second class advice
        aspect5C2.apply(self.A)

        # check everything still works
        self.assertEquals(a.x, 9)
        a.x = 3
        self.assertEquals(a.x, 13)
        a.x = 4
        self.assertEquals(a.x, 17)
        self.assertEquals(a.f(3, 4), (a, 20, 4))
        self.assertEquals(a.h(0), 3)
        self.assertEquals(a.k(0), 3) # test order of execution

        self.assertEquals(a2.x, 8) # x get?
        a2.x = 3
        self.assertEquals(a2.x, 12) # x set?
        a2.x = 4
        self.assertEquals(a2.x, 16) # x set still worked?
        self.assertEquals(a2.f(3, 4), (a2, 20, 0)) # f works?
        self.assertEquals(a2.h(0), 2)
        self.assertEquals(a2.k(0), 2) # test order of execution

        # second instance advice (again on 'a')
        aspect5I2.apply(a)

        # check everything still works
        a.x = 3 # note: last __x == 9
        self.assertEquals(a.x, 1092)
        a.x = 4
        self.assertEquals(a.x, 17476)
        self.assertEquals(a.f(3, 4), 5)
        self.assertEquals(a.h(0), 4)
        self.assertEquals(a.k(0), 4) # test order of execution

        # other instance is unaffected by a's instance advice?
        a2.x = 3
        self.assertEquals(a2.x, 12) # x set?
        a2.x = 4
        self.assertEquals(a2.x, 16) # x set still worked?
        self.assertEquals(a2.f(3, 4), (a2, 20, 0)) # f works?
        self.assertEquals(a2.h(0), 2)
        self.assertEquals(a2.k(0), 2) # test order of execution

        # works on a completely new instance?
        a2 = self.A()
        self.assertEquals(a2.x, 8) # x get?
        a2.x = 3
        self.assertEquals(a2.x, 12) # x set?
        a2.x = 4
        self.assertEquals(a2.x, 16) # x set still worked?
        self.assertEquals(a2.f(3, 4), (a2, 20, 0)) # f works?
        self.assertEquals(a2.h(0), 2)
        self.assertEquals(a2.k(0), 2) # test order of execution

    def test_6_implicits(self):
        '''test advising something like len(a)'''
        # instance advice to implicit
        a = self.A()
        aspect6.apply(a)
        self.assertEquals(len(a), 2)
        self.assertEquals(a.__len__(), 2)


from pytilities.overloading import overloaded, Overload, Param
from pytilities.types import NumberType
class B(object, metaclass=AOPMeta):
    def __init_xy(self, x, y):
        return "xy", self, x, y

    def __init_storage(self, storage):
        return "storage", self, storage

    @overloaded((
        Overload(__init_xy,
            Param("x", NumberType, default=0),
            Param("y", NumberType, default=0)),
        Overload(__init_storage,
            Param("storage"))))
    def say_ni(self):
        """docstring is docstring"""
        pass

class AspectOverload(Aspect):

    '''
    Advise an overloaded attrib and do something different for diff overloads
    '''

    def __init__(self):
        Aspect.__init__(self)
        self._advise('say_ni', call = self.advice)

    def advice(self):
        args, kwargs = yield arguments
        f = yield advised
        kwargs, f = f.process_args(*args, kwargs=kwargs)
        if f.__name__ == '__init_xy':
            kwargs["x"] = 3
        else:
            kwargs['storage'] = 3

        yield proceed(kwargs=kwargs)

aspect_overload = AspectOverload()

class OverloadTest(unittest.TestCase):
    def test_overload(self):
        '''Test aop works well together with our overloading lib'''
        aspect_overload.apply(B)

        b = B()
        self.assertEquals(b.say_ni(2, 4), ('xy', b, 3, 4))
        self.assertEquals(b.say_ni('uu'), ('storage', b, 3))

# Note: you can only advise things that have the AOPMeta on them

# TODO 
# - test that __getattr__, __setattr__, __delattr__, __getattribute__, on an
#   aop class with aopmeta (all these should be able to be used, you'll have to
#   change your meta code so that it still occasionally calls the original
#   __*attr funcs; note that __getattr__ always works, instead beware of
#   __getattribute__
#
# - Tests with inheritance (with AOPMeta, and with plain descs):
#   make an AOPMeta class A, B inherits A. Are attribs on A still
#   visible from B? i.e. with A.x = 5, is B.x 5, and is b.x as well?
#   ...
#
# - test aop.obj, aop.name commands
# - test View (copy from immutable)
# - test is* methods on aspect (just on aspect will do)
# - test implicits
# - test class advice on classes (class methods etc? more classy attribness)
# - test advisor.unapply_all
