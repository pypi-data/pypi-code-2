# -*- coding: utf-8 -*-
from utils import flatten

def init(hooksNames, hooks={}, cfg={}):

    def hook(evt, val):
        " Вызов перехватчиков "
        return reduce(
            lambda v, x: x(v), 
            hooks.get(evt, []), 
            val)

    def impHook(hookName):
        exec("from %s import maker" % hookName) in locals()
        return maker(cfg, hook)

    for k, v in flatten(map(impHook, hooksNames)):
        hooks.setdefault(k, [])
        hooks[k].append(v)

    return hook
