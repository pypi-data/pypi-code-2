#!/bin/env python

"""
This module extends Abstract base classes with the following
abilities: abstract checking for class definitions, verbose
errors with docstrings inside and abstract static and class methods

>>> class AbstractTest(object):
...     __metaclass__ = ABCMeta
...
...     @abstractmethod
...     def test(self):
...         ''' Example docstring '''
...         pass
...
...     @durable_abstractmethod
...     def test_durable(self):
...         pass
...
...     @durable_abstractmethod
...     @staticmethod
...     def test_static():
...         ''' Static docstring are UNSUPPORTED '''
...         pass
...
...     @durable_abstractmethod
...     @classmethod
...     def test_class(cls):
...         ''' classmethod docstring are UNSUPPORTED '''
...         pass

>>> a = AbstractTest() #doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
TypeError: Can't instantiate class 'AbstractTest' with 3 abstract methods: test, Decorated method 'classmethod', Decorated method 'staticmethod'

>>> class ConcreteTest(AbstractTest):
...     flag = 100
...     def test(self):
...         return 1
...
...     @staticmethod
...     def test_static():
...         return 2
...
...     def test_durable(self):
...         pass
...
...     @classmethod
...     def test_class(cls):
...         ''' classmethod docstring are UNSUPPORTED '''
...         return cls.flag

>>> ConcreteTest.test_static()
2

>>> ConcreteTest.test_class()
100

>>> b = ConcreteTest()

>>> AbstractTest.test(b)

>>> AbstractTest.test_durable(b) #doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
EAbstractFunctionCall: Call to abstract method

>>> b.test()
1

>>> class StrictAbstractTest(object):
...     __metaclass__ = ABCStrictMeta
...
...     @abstractmethod
...     def test(self):
...         ''' Example docstring '''
...         pass
...
...     @durable_abstractmethod
...     @staticmethod
...     def test_static():
...         ''' Static docstring are UNSUPPORTED '''
...         pass
...
...     @durable_abstractmethod
...     @classmethod
...     def test_class(cls):
...         ''' classmethod docstring are UNSUPPORTED '''
...         pass

>>> class FailStrictTest(StrictAbstractTest):
...     pass
Traceback (most recent call last):
TypeError: Can't define class 'FailStrictTest' with 3 abstract methods: test, Decorated method 'classmethod', Decorated method 'staticmethod'

>>> class PassAbstractTest(StrictAbstractTest):
...     def test(self):
...         ''' Example docstring '''
...         pass
...
...     @staticmethod
...     def test_static():
...         ''' Static docstring are UNSUPPORTED '''
...         pass
...
...     @classmethod
...     def test_class(cls):
...         ''' classmethod docstring are UNSUPPORTED '''
...         pass

Here is verbose variant:

>>> class AbstractTestV(object):
...     __metaclass__ = ABCMetaVerbose
...
...     @abstractmethod
...     def test(self):
...         pass
...
...     @durable_abstractmethod
...     @staticmethod
...     def test_static():
...         pass
...
...     @durable_abstractmethod
...     @classmethod
...     def test_class(cls):
...         pass

>>> a = AbstractTestV() #doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
TypeError: Can't instantiate class 'AbstractTestV' with 3 abstract methods
<BLANKLINE>
* test:
 |  Undocumented
<BLANKLINE>
* Decorated method 'classmethod':
 |  classmethod(function) -> method
 |
 |  Convert a function to be a class method.
 |
 |  A cla...
<BLANKLINE>
* Decorated method 'staticmethod':
 |  staticmethod(function) -> method
 |
 |  Convert a function to be a static method.
 |
 |  A s...

>>> class StrictAbstractTestV(object):
...     __metaclass__ = ABCStrictMetaVerbose
...
...     @abstractmethod
...     def test(self):
...         pass
...
...     @durable_abstractmethod
...     @staticmethod
...     def test_static():
...         pass
...
...     @durable_abstractmethod
...     @classmethod
...     def test_class(cls):
...         pass

>>> class FailStrictTest(StrictAbstractTestV):
...     pass
Traceback (most recent call last):
TypeError: Can't define class 'FailStrictTest' with 3 abstract methods
<BLANKLINE>
* test:
 |  Undocumented
<BLANKLINE>
* Decorated method 'classmethod':
 |  classmethod(function) -> method
 |
 |  Convert a function to be a class method.
 |
 |  A cla...
<BLANKLINE>
* Decorated method 'staticmethod':
 |  staticmethod(function) -> method
 |
 |  Convert a function to be a static method.
 |
 |  A s...
"""

from abc import ABCMeta as _ABCMeta
from abc import abstractmethod

class EAbstractFunctionCall(Exception):
    def __init__(self, fn, *args, **kwargs):
        self.__path = "%s" % (fn.__module__, )
        self.__name = fn.__name__
        self.__args = args
        self.__kwargs = kwargs

        Exception.__init__(self, self.__repr__())

    def __repr__(self):
        return "Call to abstract method '%s(%s, %s)' at '%s'" % (self.__name,
                                                                 str(self.__args),
                                                                 str(self.__kwargs),
                                                                 self.__path)

def durable_abstractmethod(f):
    #def dummy(*args, **kwargs):
    #    return f(*args, **kwargs)
    #print dir(f), f, str(f), repr(f), type(f), type(f).__name__
    #dummy = lambda *args, **kwargs : f(*args, **kwargs)
    def dummy(*args, **kwargs):
        raise EAbstractFunctionCall(f, *args, **kwargs)

    dummy.__doc__ = f.__doc__
    if hasattr(f, "__name__"):
        dummy.__name__ = f.__name__
    else:
        dummy.__name__ = type(f).__name__
    dummy.__decorated__ = f
    return abstractmethod(dummy)

class ABCMeta(_ABCMeta):
    _verbose = False

    def __call__(cls, *args, **kwargs):
        try:
            return _ABCMeta.__call__(cls, *args, **kwargs)
        except TypeError, e:
            if hasattr(cls, "__abstractmethods__"):
                abstracts = map(lambda name: getattr(cls, name), cls.__abstractmethods__)
                cls._raise_error(cls.__name__, "instantiate", abstracts)
            else:
                raise e

    @classmethod
    def _raise_error(cls, name, description, abstracts):
        separator = ": "
        if cls._verbose:
            separator = "\n\n"
        text = "Can't %s class '%s' with %d abstract methods%s" % (
            description,
            name,
            len(abstracts),
            separator
            )
        text += cls._format_problems(abstracts)
        raise TypeError(text)

    @classmethod
    def _format_problems(cls, abstracts):
        print cls, cls._verbose
        descriptions = map(lambda m: cls.__format_problem(m), abstracts)
        if cls._verbose:
            return '\n\n'.join(descriptions)
        return ', '.join(descriptions)

    @classmethod
    def __format_problem(cls, method):
        methodname = method.__name__

        if hasattr(method, "__decorated__"):
            methodname = "Decorated method '%s'" % method.__name__

        if cls._verbose:
            docstring = method.__doc__
            if not docstring:
                docstring = "Undocumented"
            lines = docstring.splitlines()
            lines = map(lambda s: " |  %s" % s, lines)
            docstring = '\n'.join(lines)
            maxlen = 100
            if len(docstring) > maxlen:
                docstring = "%s..." % docstring[:maxlen]
            return "* %s:\n%s" % (methodname, docstring)
        else:
            return methodname

class ABCStrictMeta(ABCMeta):
    def __new__(cls, name, bases, ns, *args, **kwargs):
        problems = []
        for base in bases:
            if hasattr(base, "__abstractmethods__"):
                for abstract in base.__abstractmethods__:
                    if abstract in ns:
                        pass
                    else:
                        problems.append(getattr(base, abstract))
        if problems:
            cls._raise_error(name, "define", problems)

        return _ABCMeta.__new__(cls, name, bases, ns, *args, **kwargs)

class ABCMetaVerbose(ABCMeta):
    _verbose = True

class ABCStrictMetaVerbose(ABCStrictMeta):
    _verbose = True

if __name__ == "__main__":
    import doctest
    doctest.testmod()
