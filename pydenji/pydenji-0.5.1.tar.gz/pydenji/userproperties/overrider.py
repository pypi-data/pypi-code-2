#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.
from configobj import ConfigObj
from pydenji._aop.intercept import intercept

# TODO: change this name, I don't like it.
class override_with(object):
    def __init__(self, configobj_source, *other_co_srcs):
        self._co = ConfigObj(configobj_source, unrepr=True)
        for other_src in other_co_srcs:
            self._co.merge(ConfigObj(other_src, unrepr=True))

    def __call__(self, config_cls):
        for section_name in self._co.sections:
            def section_interceptor(context):
                o = context.proceed()
                for k, v in self._co[section_name].items():
                    setattr(o, k, v)
                return o
            # this creates a new subclass every time! we should change the way
            # intercept works??
            config_cls = intercept(config_cls, section_name, section_interceptor)

        return config_cls
