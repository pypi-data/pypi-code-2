#!/bin/env python

"""
This module provides ability to create Python singletons
 as we used to do it in other languages.

>>> class Bar(Singleton):
...     def __init__(self):
...         self.b = 14
...     def h(self):
...         print 12
...     def __getattr__(self, name):
...        print 'logger:', name
...
>>> class Bar2(object):
...     __metaclass__ = SingletonMeta
...
>>> class Foo(object):
...     __metaclass__ = SingletonMeta
...     def __init__(self, a):
...         self.a = a
...         print 'Inited! Arg:', self.a
...     def hey(self):
...         print 'Hey! Arg:', self.a
...     def calc(self, b):
...         return self.a + b
...
>>> Foo(1).hey()
Inited! Arg: 1
Hey! Arg: 1
>>> Foo().hey()
Hey! Arg: 1
>>> Foo() == Foo()
True
>>> a = Foo()
>>> a.calc(3) == 4
True
>>> Foo().calc(2) == a.calc(2)
True
>>> Bar() == Bar()
True
>>> Bar2() == Bar2()
True
>>> Bar2() == Bar()
False
>>> Foo() == Bar()
False
>>> Foo.a
1
>>> Bar.b
14
>>> Bar.core
logger: core
"""

class SingletonMeta(type):
    def __init__(cls, name, bases, dict):
        super(SingletonMeta, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(self,*args,**kw):
        if self.instance is None:
            self.instance = super(SingletonMeta, self).__call__(*args, **kw)
        return self.instance

    def __getattr__(cls, name): #@NoSelf
        return getattr(cls(), name)

class Singleton(object):
    __metaclass__ = SingletonMeta


if __name__ == "__main__":
    import doctest
    doctest.testmod()
