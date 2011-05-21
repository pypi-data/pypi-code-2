#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni. APL 2.0 licensed.

from unittest import TestCase
from abc import abstractmethod

from ducktypes.funcwrapper import copy_func

@abstractmethod
def example_func(a, b, c=1):
    return 1

class TestFuncWrapper(TestCase):
    def test_function_wrapper_preserves_function_arg_count(self):
        wrapped = copy_func(example_func)
        self.assertEquals(3, wrapped.func_code.co_argcount)

    def test_function_wrapper_preserves_function_return_value(self):
        wrapped = copy_func(example_func)
        self.assertEquals(1, wrapped(1,2))

    def test_wrapped_function_is_never_abstract(self):
        wrapped = copy_func(example_func)
        self.assertFalse(getattr(wrapped, "__isabstractmethod__", False))