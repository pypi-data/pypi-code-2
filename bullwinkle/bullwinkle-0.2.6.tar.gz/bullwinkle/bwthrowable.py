'''
bwthrowable -- throw and catch objects on the stack

Provides a means to send contextual objects to called frames.  Thrown
variables are stored based on their Python type so that they may be caught
either the type of a subtype.

For example, consider an HTTP request class:
>>> class HTTPRequest(BWThrowable):
...     def __init__(self, method, path):
...         self.method = method
...         self.path = path
...

It is often the case that a web framework will define one and want to send
it along as context.  Often it is inconvenient to send the context as
parameters to all called functions, so:

>>> req = HTTPRequest('GET', '/index.html')
>>> req.throw()

Now any function that needs access to the request but cannot acquire it by
parameter can pick it up using .catch():

>>> def controller():
...     req = HTTPRequest.catch()
...     print req.path
...
>>> controller()
/index.html

The throw part can be skipped via with statements:

>>> with HTTPRequest('GET', '/image/pic.png') as req:
...     controller()
...
/image/pic.png

In addition, individual keys can be thrown and caught, though throw() is
optional if the key name is a simple string:

>>> def catcher(name):
...     print catch(name)
...
>>> throw('x', 5)
>>> catcher('x')
5
>>> x = 7
>>> catcher('x')
7
'''

from __version__ import *
import sys

def throw(key, value, frame=0):
    sys._getframe(frame + 1).f_locals[key] = value

def catch(key, default=None, NOT_FOUND=KeyError):
    f = sys._getframe(1)
    while f is not None:
        obj = f.f_locals.get(key, NOT_FOUND)
        if obj is not NOT_FOUND:
            return obj
        f = f.f_back
    else:
        return default

class BWThrowableNotFoundError(Exception):
    def __init__(self, cls):
        self.cls = cls

class BWThrowable(object):
    def throw(self, frame=0):
        sys._getframe(frame + 1).f_locals[type(self)] = self
    __enter__ = throw

    @classmethod
    def catch(cls):
        top = sys._getframe(1)
        for base in cls.__mro__:
            f = top
            while f is not None:
                obj = f.f_locals.get(base)
                if obj is not None:
                    return obj
                else:
                    f = f.f_back
        else:
            return self.uncaught()

    @classmethod
    def uncaught(cls):
        return cls()

    class DefaultNone(object):
        @classmethod
        def uncaught(self):
            return None

    class DefaultError(object):
        error_type = BWThrowableNotFoundError

        @classmethod
        def uncaught(cls):
            raise error_type(cls)

    def __exit__(self, *_args):
        pass

