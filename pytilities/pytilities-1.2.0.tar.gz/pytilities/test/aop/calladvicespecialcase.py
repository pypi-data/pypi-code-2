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
from pytilities.aop import Aspect

class CallAdviceSpecialCaseTest(unittest.TestCase):

    def setUp(self):
        class A(object):
            def f(s):
                return s

        class AspectA(Aspect):
            def __init__(s):
                Aspect.__init__(s)
                s._advice_mappings['get', 'f'] = s._advice
                s._advice_mappings['call', 'f'] = s._advice
                s.reset()

            def reset(s):
                s.last_arguments = None
                s.last_obj = None

            def _advice(s):
                s.last_arguments = yield aop.arguments
                s.last_obj = yield aop.advised_instance
                yield aop.proceed

        class B(object): pass

        class AspectB(Aspect):
            def __init__(s):
                Aspect.__init__(s)
                s._advice_mappings['get', 'f'] = s._advice
                s._advice_mappings['call', 'f'] = s._advice_call
                s.reset()

            def reset(s):
                s.last_arguments = None
                s.last_obj = None

            def _advice(s):
                s.last_arguments = yield aop.arguments
                s.last_obj = yield aop.advised_instance
                yield aop.return_(self.a.f)

            def _advice_call(s):
                s.last_arguments = yield aop.arguments
                yield aop.proceed

        self.a = A()
        self.aspectA = AspectA()
        self.aspectA.apply(self.a)

        self.b = B()
        self.aspectB = AspectB()
        self.aspectB.apply(self.b)

    def test_it(self):
        self.assertIsNotNone(self.when_get())
        self.then_aspect_executed(self.aspectA, args=(self.a,), obj=self.a)
        self.then_aspect_executed(self.aspectB, args=(self.b,), obj=self.b)

        self.assertIs(self.a, self.when_call())
        self.then_aspect_executed(self.aspectA, args=(self.a,), obj=self.a)
        self.then_aspect_not_executed(self.aspectB)

    def when_get(self):
        return self.b.f

    def when_call(self):
        f = self.b.f
        self.aspectA.reset()
        self.aspectB.reset()
        return f()

    def then_aspect_executed(self, aspect, args, obj):
        self.assertEqual((args, {}), aspect.last_arguments)
        self.assertIs(obj, aspect.last_obj)

    def then_aspect_not_executed(self, aspect):
        self.assertEqual(None, aspect.last_arguments)

