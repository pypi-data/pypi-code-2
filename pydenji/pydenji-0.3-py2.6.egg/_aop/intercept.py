#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

"""
Basic interception package.

This is intended for internal usage only by the config package.

Evaluate different solutions (aspyct, pyaop) for everyday use.

This system uses dynamic subclassing. Original classes are untouched.
"""
# TODO: check class vs instance interception. -> are classmethods intercepted correctly?
# TODO: let interception not to depend on our context object, but use standard function args?

class _Context(object):
    def __init__(self, instance, method, args, kwargs):
        self.instance = instance
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def proceed(self):
        return self.method(self.instance, *self.args, **self.kwargs)

def _interceptor(original_method, method_interceptor):
    def intercepted(instance, *args, **kwargs):
        return method_interceptor(_Context(instance, original_method, args, kwargs))
    return intercepted

def intercept(cls, method_name, method_interceptor):
    # interceptor result will be returned. no auto-return of original method
    # return value will be performed.
    original_method = getattr(cls, method_name)
    intercepted = _interceptor(original_method, method_interceptor)
    return type(cls)(cls.__name__, (cls, ), {method_name:intercepted} )
    





