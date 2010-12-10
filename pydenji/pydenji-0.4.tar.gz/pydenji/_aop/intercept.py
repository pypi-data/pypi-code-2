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
    def __init__(self, method, args, kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def proceed(self):
        return self.method(*self.args, **self.kwargs)


def _update_func_dict(source, dest):
    dest.__dict__.update(source.__dict__)
    return dest
    
def _interceptor_picker(original_method, method_interceptor):
    # picks the proper interceptor depending on original_method type.
    if getattr(original_method, "im_func", None):
        if getattr(original_method, "im_self"):
            return _classmethod_interceptor(original_method, method_interceptor)
        else:
            return _instancemethod_interceptor(original_method, method_interceptor)
    else:
        return _staticmethod_interceptor(original_method, method_interceptor)

def _staticmethod_interceptor(original_staticmethod, method_interceptor):
    def intercepted(*args, **kwargs):
        return method_interceptor(_Context(original_staticmethod, args, kwargs))
    return staticmethod(_update_func_dict(original_staticmethod, intercepted))

def _classmethod_interceptor(original_classmethod, method_interceptor):
    def intercepted(cls, *args, **kwargs):
        # we must not pass cls in args since classmethod will bind it.
        return method_interceptor(_Context(original_classmethod, args, kwargs))
    return classmethod(_update_func_dict(original_classmethod, intercepted))

def _instancemethod_interceptor(original_method, method_interceptor):
    def intercepted(instance, *args, **kwargs):
        return method_interceptor(_Context(original_method, (instance, ) + args, kwargs))
    return _update_func_dict(original_method, intercepted)

def intercept(cls, method_name, method_interceptor):
    # interceptor result will be returned. no auto-return of original method
    # return value will be performed.
    original_method = getattr(cls, method_name)
    intercepted = _interceptor_picker(original_method, method_interceptor)
    
    return type(cls)(cls.__name__, (cls, ), {method_name:intercepted} )
    





