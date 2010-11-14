# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest

from pydenji._aop.intercept import intercept

class TestInterception(unittest.TestCase):
    class MyTestClass(object):
        def __init__(self, arg):
            self.arg = arg

        def method(self, value):
            return self.arg + value


    # TODO: split those tests into multiple tests!
    def test_init_interception(self):
        def init_interceptor(context):
            self.assertRaises(AttributeError, getattr, context.instance, "arg")
            context.proceed()
            context.instance.other_arg = 5
           

        intercepted = intercept(self.MyTestClass, "__init__", init_interceptor)
        test_obj = intercepted(3)
        self.assertEquals(3, test_obj.arg)
        self.assertEquals(5, test_obj.other_arg)


    def test_method_interception(self):
        def method_interceptor(context):
            value = context.proceed()
            return value * 4

        intercepted = intercept(self.MyTestClass, "method", method_interceptor)
        test_obj = intercepted(3)
        self.assertEquals((3 + 5) * 4, test_obj.method(5))




