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
import inspect
import pdb

from pytilities import aop
from pytilities.aop import (
    Aspect, AOPException, advisor, AOPMeta
)

class AspectTest(unittest.TestCase):

    '''Tests aspect usage, apply order, ...'''

    def test_get_applied_aspects(self):
        self.then_applied_aspects(A)
        self.then_applied_aspects(a1)
        self.then_applied_aspects(a2)

        aspect1.apply(A)
        self.then_applied_aspects(A, aspect1)
        self.then_applied_aspects(a1, aspect1)
        self.then_applied_aspects(a2, aspect1)

        aspect2.apply(a1)
        self.then_applied_aspects(A, aspect1)
        self.then_applied_aspects(a1, aspect1, aspect2)
        self.then_applied_aspects(a2, aspect1)

    def test_get_applied_aspects2(self):
        aspect1.apply(a1)
        aspect2.apply(a1)
        self.then_applied_aspects(A)
        self.then_applied_aspects(a1, aspect1, aspect2)
        self.then_applied_aspects(a2)

    def test_unapply_all(self):
        self.then_applied_aspects(a1)

        advisor.unapply_all(a1)
        self.then_applied_aspects(a1)

        aspect1.apply(a1)
        advisor.unapply_all(a1)
        self.then_applied_aspects(a1)

        aspect1.apply(a1)
        aspect2.apply(a1)
        advisor.unapply_all(a1)
        self.then_applied_aspects(a1)

        aspect1.apply(A)
        aspect2.apply(a1)
        advisor.unapply_all(a1)
        self.then_applied_aspects(a1)
        self.then_applied_aspects(a2, aspect1)

        #aspect1.apply(A)
        aspect2.apply(a1)
        advisor.unapply_all(A)
        self.then_applied_aspects(A)
        self.then_applied_aspects(a1)

    def test_advice_class(self):
        self.when_apply_aspects(A, aspect1)
        self.then_applied_aspects(A, aspect1)
        self.then_applied_aspects(a1, aspect1)
        self.then_applied_aspects(a2, aspect1)

    def test_advice_instance(self):
        self.when_apply_aspects(a1, aspect1)
        self.then_applied_aspects(a2)

    def test_unapply(self):
        self.when_apply_aspects(a1, aspect1)
        aspect1.unapply(a1)
        self.then_applied_aspects(a1)

    def test_unapply2(self):
        self.when_apply_aspects(A, aspect1)
        aspect1.unapply(A)
        self.then_applied_aspects(a1)

    def test_unapply3(self):
        self.when_apply_aspects(a1, aspect1)
        aspect1.unapply(A)
        self.then_applied_aspects(a1)

    def test_apply(self):
        aspect1.apply(A)
        aspect1.apply(a1)
        self.then_applied_aspects(A, aspect1)
        self.then_applied_aspects(a1, aspect1)

    def test_apply2(self):
        aspect1.apply(a1)
        aspect1.apply(A)
        self.then_applied_aspects(A, aspect1)
        self.then_applied_aspects(a1, aspect1)

    def test_apply_unapply(self):
        self.when_apply_aspects(a1, aspect1, aspect2)

        aspect2.apply(A)
        self.then_applied_aspects(a1, aspect2, aspect1)
        self.then_applied_aspects(a2, aspect2)

        aspect2.unapply(a1)
        self.then_applied_aspects(a1, aspect1)
        self.then_applied_aspects(a2, aspect2)

        aspect2.apply(a1)
        self.then_applied_aspects(A, aspect2)
        self.then_applied_aspects(a1, aspect2, aspect1)
        self.then_applied_aspects(a2, aspect2)

        aspect2.unapply(A)
        self.then_applied_aspects(a1, aspect1)
        self.then_applied_aspects(a2)

    def test_apply_multiple_advice(self):
        self.when_apply_aspects(a1, aspect1, aspect2)

    def test_unapply_of_multiple_advice(self):
        self.when_apply_aspects(a1, aspect1, aspect2)
        aspect1.unapply(a1)
        self.then_applied_aspects(a1, aspect2)
        aspect1.apply(a1)
        self.then_applied_aspects(a1, aspect2, aspect1)

    def test_apply_twice(self):
        self.when_apply_aspects(a1, aspect1)
        aspect1.apply(a1)
        self.then_applied_aspects(a1, aspect1)
        # Note: this sort of behaviour allows not having to know about what is
        # currently applied to an object, which is mighty handy

    def test_unapply_the_unapplied(self):
        aspect1.unapply(a1)
        self.then_applied_aspects(a1)
        # Note: this sort of behaviour allows not having to know about what is
        # currently applied to an object, which is mighty handy

    def test_enabled_default(self):
        self.when_apply_aspects(a1, aspect1, aspect2)
        self.when_apply_aspects(a2, aspect1)
        self.then_is_enabled(a1, aspect1, aspect2)
        self.then_is_enabled(a2, aspect1)

    def test_disable(self):
        self.when_apply_aspects(a1, aspect1, aspect2)
        self.when_apply_aspects(a2, aspect1)

        aspect1.disable(a1)
        self.then_is_enabled(a1, aspect2)
        self.then_affecting_aspects(a1, aspect2)
        self.then_is_enabled(a1, aspect1, enabled=False)
        self.then_is_enabled(a2, aspect1)
        self.then_affecting_aspects(a2, aspect1)

        aspect1.enable(a1)
        self.then_is_enabled(a1, aspect1, aspect2)
        self.then_affecting_aspects(a1, aspect1, aspect2)
        self.then_is_enabled(a2, aspect1)
        self.then_affecting_aspects(a2, aspect1)

    def test_disable_twice(self):
        self.when_apply_aspects(a1, aspect1)
        aspect1.disable(a1)
        aspect1.disable(a1)
        self.then_is_enabled(a1, aspect1, enabled=False)
        aspect1.enable(a1)
        self.then_is_enabled(a1, aspect1)

    def test_enable_twice(self):
        self.when_apply_aspects(a1, aspect1)
        aspect1.enable(a1)  #default is being enabled
        self.then_is_enabled(a1, aspect1)
        aspect1.disable(a1)
        self.then_is_enabled(a1, aspect1, enabled=False)

    def test_aspect_is_enabled_after_apply(self):
        self.when_apply_aspects(a1, aspect1)

        aspect1.disable(a1)
        self.then_is_enabled(a1, aspect1, enabled=False)
        self.then_affecting_aspects(a1)

        aspect1.unapply(a1)
        aspect1.apply(a1)
        self.then_is_enabled(a1, aspect1)
        self.then_affecting_aspects(a1, aspect1)

    def test_enableness_when_unapplied(self):
        self.assertFalse(aspect1.is_enabled(a1))

        with self.assertRaises(AOPException):
            aspect1.enable(a1)

        with self.assertRaises(AOPException):
            aspect1.disable(a1)

    def test_advise_star_to_class(self): #  * advice
        self.when_apply_aspects(Meta, aspectStar)
        self.then_applied_aspects(meta, aspectStar)

    def test_advise_star_to_instance(self):
        self.when_apply_aspects(meta, aspectStar)
        self.then_applied_aspects(meta, aspectStar)

    def test_bad_advice(self):
        class AnAspect(Aspect):
            def __init__(s, f):
                Aspect.__init__(s)
                f(s)

        def advice1():
            yield aop.return_

        def advice2():
            yield aop.return_

        with self.assertRaises(AOPException):
            def f(s):
                s._advise('*', get=advice1)
                s._advise('normal_member', get=advice2)
            AnAspect(f)

        with self.assertRaises(AOPException):
            def f(s):
                s._advise('normal_member', get=advice1)
                s._advise('*', get=advice2)
            AnAspect(f)

        with self.assertRaises(AOPException):
            def f(s):
                s._advise('normal_member', get=advice1)
                s._advise('normal_member', get=advice2)
            AnAspect(f)

        # this is good advising
        def g(s):
            s._advise('normal_member', set_=advice1)
            s._advise('*', get=advice1, delete=advice1,
                      call=advice1)
        AnAspect(g)


    def when_apply_aspects(self, to, *aspects):
        for aspect in aspects:
            aspect.apply(to)
            self.then_applied_aspects(to, *advisor.get_applied_aspects(to))
            self.then_is_enabled(to, aspect)

    def _then_is_applied(self, to, aspect, applied=True):
        self.assertEquals(applied, aspect.is_applied(to))

    def then_is_enabled(self, for_, *aspects, enabled=True):
        for aspect in aspects:
            self.assertEquals(enabled, aspect.is_enabled(for_))

    def reset_aspects(self):
        for aspect in all_aspects: 
            aspect.reset()

    def _get_numbered_sequence(self, affected_aspects):
        numbered_aspects = {aspect : 0  
            for aspect 
            in all_aspects 
            if aspect not in affected_aspects}

        numbered_affected_aspects = {aspect : index+1 
            for index, aspect 
            in enumerate(reversed(affected_aspects))}

        numbered_aspects.update(numbered_affected_aspects)
        return numbered_aspects

    def _then_aspects_affected_get_like(self, aspects):
        for aspect, sequence_number in self._get_numbered_sequence(aspects).items():
            self.assertEquals(sequence_number, aspect.affected_get_at)
            self.assertEquals(0, aspect.affected_set_at)
            self.assertEquals(0, aspect.affected_del_at)
            self.assertEquals(0, aspect.affected_call_at)
        self.reset_aspects()

    def _then_aspects_affected_set_like(self, aspects):
        for aspect, sequence_number in self._get_numbered_sequence(aspects).items():
            self.assertEquals(0, aspect.affected_get_at)
            self.assertEquals(sequence_number, aspect.affected_set_at)
            self.assertEquals(0, aspect.affected_del_at)
            self.assertEquals(0, aspect.affected_call_at)
        self.reset_aspects()

    def _then_aspects_affected_del_like(self, aspects):
        for aspect, sequence_number in self._get_numbered_sequence(aspects).items():
            self.assertEquals(0, aspect.affected_get_at)
            self.assertEquals(0, aspect.affected_set_at)
            self.assertEquals(sequence_number, aspect.affected_del_at)
            self.assertEquals(0, aspect.affected_call_at)
        self.reset_aspects()

    def _then_aspects_affected_call_like(self, aspects):
        call_offset = len(aspects)
        for aspect, sequence_number in self._get_numbered_sequence(aspects).items():
            self.assertEquals(sequence_number, aspect.affected_get_at)
            self.assertEquals(0, aspect.affected_set_at)
            self.assertEquals(0, aspect.affected_del_at)
            if (sequence_number == 0):
                self.assertEquals(0, aspect.affected_call_at)
            else:
                self.assertEquals(call_offset+sequence_number,
                                  aspect.affected_call_at)
        self.reset_aspects()

    def then_applied_aspects(self, to, *by):
        self.assertEquals(by, tuple(advisor.get_applied_aspects(to)))
        for aspect in by:
            self._then_is_applied(to, aspect)

        self.then_affecting_aspects(to, *by)

    def then_affecting_aspects(self, to, *by):
        obj = to
        aspects = by
        if inspect.isclass(obj):
            return 

        obj.reset(self)
        self.reset_aspects()

        obj.x = 3
        self._then_aspects_affected_set_like(aspects)
        if (aspectStar in aspects):
            obj.x
        else:
            self.assertEquals(3, obj.x)
        self._then_aspects_affected_get_like(aspects)

        del obj.x
        self._then_aspects_affected_del_like(aspects)
        obj.f()
        self._then_aspects_affected_call_like(aspects)

        if (aspects):
            # only last one counts as no proceeds are done
            last_aspect = (aspects[-1],)
            obj.unexisting = 3
            self._then_aspects_affected_set_like(last_aspect)
            self.assertIsNotNone(obj.unexisting)
            self._then_aspects_affected_get_like(last_aspect)
            del obj.unexisting
            self._then_aspects_affected_del_like(last_aspect)
            obj.unexisting()
            self._then_aspects_affected_call_like(last_aspect)

    def tearDown(self):
        advisor.unapply_all(A)
        advisor.unapply_all(Meta)
        self.then_applied_aspects(A)
        self.then_applied_aspects(a1)
        self.then_applied_aspects(a2)
        self.then_applied_aspects(Meta)
        self.then_applied_aspects(meta)

class A(object):

    def reset(self, test):
        self.__x = 0

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @x.deleter
    def x(self):
        self.__x = 'deleted'

    def f(self):
        pass

class Meta(A, metaclass=AOPMeta):
    pass

class AspectA(Aspect):

    def __init__(self):
        Aspect.__init__(self)
        self._advise('x', 'f', get=self._affect_get, set_=self._affect_set,
                     delete=self._affect_del, call=self._affect_call)
        self._advise('unexisting', 
                     get=self._affect_unexisting_get,
                     set_=self._affect_unexisting_set,
                     delete=self._affect_unexisting_del, 
                     call=self._affect_unexisting_call)
        self.reset()

    def reset(self):
        AspectA.sequence_number = 0
        # when these were affected, 0 means never, 1 first, 2 second, ...
        self.affected_get_at= self.affected_set_at = 0  
        self.affected_del_at = self.affected_call_at = 0

    def __get_next_sequence_number(self):
        AspectA.sequence_number += 1
        return AspectA.sequence_number

    def _affect_get(self):
        self.affected_get_at= self.__get_next_sequence_number()
        yield aop.proceed

    def _affect_unexisting_get(self):
        self.affected_get_at= self.__get_next_sequence_number()
        (n, _) = yield aop.advised_attribute
        o = yield aop.advised_instance
        if n == 'reset':
            yield aop.return_(meta_reset)
        else:
            yield aop.return_(self.f)

    def f(self):
        pass

    def _affect_set(self):
        self.affected_set_at = self.__get_next_sequence_number()
        yield aop.proceed

    def _affect_unexisting_set(self):
        self.affected_set_at = self.__get_next_sequence_number()
        yield aop.return_

    def _affect_del(self):
        self.affected_del_at = self.__get_next_sequence_number()
        yield aop.proceed

    def _affect_unexisting_del(self):
        self.affected_del_at = self.__get_next_sequence_number()
        yield aop.return_

    def _affect_call(self):
        self.affected_call_at = self.__get_next_sequence_number()
        yield aop.proceed

    def _affect_unexisting_call(self):
        self.affected_call_at = self.__get_next_sequence_number()
        yield aop.return_


class StarAspect(AspectA):

    def __init__(self):
        Aspect.__init__(self)  # intentionally skipping a ctor
        self._advise('*', 
                     get=self._affect_unexisting_get,
                     set_=self._affect_unexisting_set,
                     delete=self._affect_unexisting_del, 
                     call=self._affect_unexisting_call)
        self.reset()

a1 = A()
a2 = A()
meta = Meta()
meta_reset = meta.reset
aspect1 = AspectA()
aspect2 = AspectA()
aspectStar = StarAspect()
all_aspects = (aspect1, aspect2, aspectStar)

# some old TODO's taken from the other file
# - test that __getattr__, __setattr__, __delattr__, __getattribute__, on an
#   aop class with aopmeta (all these should be able to be used, you'll have to
#   change your meta code so that it still occasionally calls the original
#   __*attr funcs; note that __getattr__ always works, instead beware of
#   __getattribute__
#
