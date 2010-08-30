#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from functools import partial
from types import UnboundMethodType

from pydenji.appcontext.aware import is_appcontext_aware

# TODO: we might probably reduce the number of constants.
_CONFIGURED_OBJECT_FACTORY = "_pydenji__CONFIGURED_OBJECT_FACTORY"
_INSTANTIATE_EAGERLY = "_pydenji__INSTANTIATE_EAGERLY"
_SHOULD_CONFIGURE = "_pydenji__SHOULD_CONFIGURE"

def is_object_factory(obj):
    if getattr(obj, _CONFIGURED_OBJECT_FACTORY, None) is True:
        return True
    return False

def is_eager(obj):
    if getattr(obj, _INSTANTIATE_EAGERLY, None) is True:
        return True
    return False

def should_be_configured(obj):
    return getattr(obj, _SHOULD_CONFIGURE, True)

class _Maybe(object):
    def __init__(self, has_value=False, value=None):
        self.has_value = has_value
        self.value = value

def singleton(func, eager=True):
    maybevalue = _Maybe()
    def singleton_wrapped(self, *args, **kwargs):
        if args or kwargs:
            raise TypeError, "Singleton mustn't take any parameter. Use per-instance config instead."

        if not maybevalue.has_value:
            maybevalue.value = func(self)
            maybevalue.has_value = True
        return maybevalue.value

    setattr(singleton_wrapped, _INSTANTIATE_EAGERLY, eager)
    setattr(singleton_wrapped, _CONFIGURED_OBJECT_FACTORY, True)
    setattr(singleton_wrapped, _SHOULD_CONFIGURE, False)

    return singleton_wrapped

singleton.lazy = partial(singleton, eager=False)

def prototype(func):
    def f(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(f, _CONFIGURED_OBJECT_FACTORY, True)
    setattr(f, _INSTANTIATE_EAGERLY, False)
    setattr(f, _SHOULD_CONFIGURE, False)
    return f

def dontconfigure(func):
    def f(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(f, _SHOULD_CONFIGURE, False)
    setattr(f, _INSTANTIATE_EAGERLY, False)
    setattr(f, _CONFIGURED_OBJECT_FACTORY, False)
    return f


def _to_be_configured(clsattr, attrvalue):
    return ((not clsattr.startswith("_")) and
        isinstance(attrvalue, UnboundMethodType) and
        not is_object_factory(attrvalue) and
        should_be_configured(attrvalue))

def Configuration(cls, configure_with=singleton, suffix="Configuration"):
    """
    Makes all public, unwrapped methods *eager singletons* by default.
    Also, after instantiation a "params" instance attribute will be set -
    it will hold a dictionary.

    Non-public methods and already-wrapped methods will just go untouched.
    """
    configured_dict = {}
    for clsattr in dir(cls):
        attrvalue = getattr(cls, clsattr)
        if _to_be_configured(clsattr, attrvalue):
            configured_dict[clsattr] = configure_with(attrvalue)
    cls_type = type(cls)
    return cls_type(cls.__name__ + suffix, (cls, ), configured_dict)








