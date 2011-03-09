#! /usr/bin/env python
#coding=utf-8
import types
import inspect
from http_exc import Http404
from urllib import unquote

class RouteType:
    module , im_class , func , im_func = range(4)


ACCESS_FUNC = "_access"
LOOKUP_FUNC = "_lookup"

class UrlMap(object):
    def __init__(self):
        self.__dict__["_urlmap"] = {}
        self.__dict__["_obj"] = None
        self.__dict__["_type"] = None
        self.__dict__["_parse"] = None
        self.__dict__["_arg_len"] = 0

    def __getattr__(self, name):
        r = self._urlmap.get(name)
        if not r:
            r = UrlMap()
            self._urlmap[name] = r
        return r

    def __lshift__(self, url):
        url = unquote(url)
        url = tuple(i for i in url.split("/") if i)
        url_length = len(url)
        now = self
        pos = 0
        temp = None
        result = None
        while 1:
            if now is None:
                raise Http404
            elif now._obj:
                arg_len = now._arg_len
                if arg_len:
                    pos_next = pos + now._arg_len
                    arg = url[pos:pos_next]
                    pos = pos_next
                else:
                    arg = ()
                is_class = now._type is RouteType.im_class
                if is_class:
                    ins = now._obj()
                else:
                    is_im_func = now._type is RouteType.im_func

                if now._parse:
                    if is_class or is_im_func:
                        result = now._parse(ins, *arg)
                    else:
                        result = now._parse(*arg)
                    if result is not None:
                        if result is False:
                            return ""
                        return result

            if pos < url_length:
                urlmap = now._urlmap
                name = url[pos]

                if name and name[0].isalpha():
                    temp = urlmap.get(name)
                if temp:
                    pos += 1
                    now = temp
                    temp = None
                else:
                    now = urlmap.get("_lookup")
            else:
                break

        if now._type is RouteType.module:
            now = now._urlmap.get("index")
            if now and now._parse:
                result = now._parse()
            else:
                raise Http404

        elif now._type is RouteType.im_class:
            now = now._urlmap.get("index")
            if now and now._parse:
                result = now._parse(result)
            else:
                raise Http404

        if result is False:
            return ""
        return result

    def __call__(self, obj):
        self._obj = obj
        obj_type = type(obj)

        if obj_type is types.FunctionType:
            self._type = RouteType.func
            self._parse = obj
            self._arg_len = obj.func_code.co_argcount

        elif obj_type is types.MethodType:
            self._type = RouteType.im_func
            self._parse = obj
            self._arg_len = obj.func_code.co_argcount-1

        elif obj_type is types.ModuleType:
            self._type = RouteType.module
            if hasattr(obj, ACCESS_FUNC):
                access = getattr(obj, ACCESS_FUNC)
                if type(access) is types.FunctionType:
                    self._parse = access
                    self._arg_len = access.func_code.co_argcount
            if hasattr(obj, LOOKUP_FUNC):
                self._lookup(getattr(obj, LOOKUP_FUNC))

        elif inspect.isclass(obj):
            self._type = RouteType.im_class
            if hasattr(obj, ACCESS_FUNC):
                self._obj = obj
                access = getattr(self._obj, ACCESS_FUNC)
                if type(access) is types.MethodType:
                    self._parse = access
                    self._arg_len = access.func_code.co_argcount-1
            if hasattr(obj, LOOKUP_FUNC):
                self._lookup(getattr(obj, LOOKUP_FUNC))
        return obj

def ltrim(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

class Route(object):
    def __init__(self):
        self.__dict__["_urlmap"] = UrlMap()
        self.__dict__["_buf"] = []

    def __lshift__(self, url):
        return self._urlmap << url.rstrip()

    def __getattr__(self, name):
        return getattr(self._urlmap, name)

    def __call__(self, obj, namespace=[]):
        self._buf.append((obj, namespace))
        return obj

    def _install(self, app, prefix=''):
        self._urlmap(app)
        for obj, namespace in self._buf:
            obj_type = type(obj)
            if obj_type in (types.FunctionType, types.MethodType):
                obj_type = type(obj)

                def mod2list(o):
                    r = o.__module__
                    r = ltrim(r, prefix)
                    r = r[len(ltrim(self._urlmap._obj.__name__, prefix)):]
                    r = r.lstrip(".").split(".")+namespace
                    return r

                if obj_type is types.FunctionType:
                    obj_prefix = mod2list(obj)
                    obj_name = obj.__name__
                elif obj_type is types.MethodType:
                    obj_prefix = mod2list(obj.im_func)
                    obj_name = obj.im_func.__name__
                obj_prefix.append(obj_name)

                now = self._urlmap
                for i in obj_prefix:
                    #print obj_prefix
                    if i:
                        next_urlmap = getattr(now, i)
                        if not next_urlmap._obj:
                            try:
                                next_urlmap(getattr(now._obj, i))
                            except:
                                print now._obj, i
                                raise
                        now = next_urlmap

            elif inspect.isclass(obj):
                for k in obj.__dict__:
                    if not k.startswith("_"):
                        self(getattr(obj, k), namespace+[obj.__name__])
        self._buf = []
