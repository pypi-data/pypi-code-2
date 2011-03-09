#coding:utf-8

from types import FunctionType
from byteplay import Code, opmap

from render import Render, render_func, render_doc, get_request
from urlroute import Route
from decorator import decorator
import inspect

_ROUTE = Route()

def _transmute(opcode, arg):
    if (
        (opcode==opmap['LOAD_GLOBAL'])
        and
        arg=='request'
    ):
        return opmap['LOAD_FAST'], arg
    return opcode, arg

def _render_para_func(func):
    code = Code.from_code(func.func_code)
    code.args = tuple(['request'] + list(code.args))
    code.code = [_transmute(op, arg) for op, arg in code.code]
    func.func_code = code.to_code()
    return func

class RequestRoute(object):
    def __call__(self, func):
        func = _ROUTE(func)
        if inspect.isclass(func):
            w = []
            for k, v in func.__dict__.iteritems():
                if not k.startswith("_") and inspect.isfunction(v):
                    w.append((k, wrap_func(v)))
            for k, v in w:
                setattr(func, k, v)
        else:
            func = wrap_func(func)
        return func

    def __getattr__(self, name):
        attr = getattr(_ROUTE, name)
        def tmp(func):
            func = wrap_func(func)
            func = attr(func)
            return func
        return tmp


route = RequestRoute()

def  _wrap_func(func, *args, **kwds):
    r = func(get_request(), *args, **kwds)
    return r

def wrap_func(func):
    f = decorator(_wrap_func, func)
    func = _render_para_func(func)
    return f

def route_render_func(func):
    if type(func) is str:
        w = render_func(func)
        return lambda f:_ROUTE(w(f))
    else:
        return _ROUTE(render_func(func))

def route_render_doc(func):
    return _ROUTE(render_doc(func))

