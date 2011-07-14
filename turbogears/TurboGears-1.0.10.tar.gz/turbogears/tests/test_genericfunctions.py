import unittest

from dispatch import generic

from turbogears.genericfunctions import *


mo_state = []

[generic(MultiorderGenericFunction)]
def mo(a):
    pass

[mo.when("a>0", order=2)]
def mo2(next_method, a):
    mo_state.append(2)

[mo.when("a>0")]
def mo0(next_method, a):
    mo_state.append(0)
    return next_method(a)

[mo.when("a>0", order=1)]
def mo1(next_method, a):
    mo_state.append(1)
    return next_method(a)

[mo.around("a<23")]
def moa0(next_method, a):
    mo_state.append("a")
    return next_method(a)

[mo.around("a<123")]
def moa1(next_method, a):
    mo_state.append("b")
    return next_method(a)


class TestGenericFunctions(unittest.TestCase):

    def test_multiorder(self):
        mo(2)
        self.failUnless(mo_state == ["a", "b", 0,1,2])

    def test_getter(self):
        foo = 123
        _get_foo = getter("foo")
        _get_bar = getter("bar")
        self.failUnless(_get_foo() == 123)
        foo = 2
        self.failUnless(_get_foo() == 2)
        bar = 67
        self.failUnless(_get_bar() == 67)
