import sys
import datetime
import pytz
import persistent
from zope import interface, event, component
import zope.annotation.interfaces
from zope.cachedescriptors.property import Lazy

from zc.freeze import interfaces
import rwproperty

def method(f):
    def wrapper(self, *args, **kwargs):
        try: # micro-optimize for the "yes, I'm already an IFreezing" story
            frozen = self._z_frozen
        except AttributeError:
            frozen = interfaces.IFreezing(self)._z_frozen
        if frozen:
            raise interfaces.FrozenError
        return f(self, *args, **kwargs)
    return wrapper

class setproperty(rwproperty.rwproperty):

    @staticmethod
    def createProperty(func):
        return property(None, method(func))

    @staticmethod
    def enhanceProperty(oldprop, func):
        return property(oldprop.fget, method(func), oldprop.fdel)

class delproperty(rwproperty.rwproperty):

    @staticmethod
    def createProperty(func):
        return property(None, None, method(func))

    @staticmethod
    def enhanceProperty(oldprop, func):
        return property(oldprop.fget, oldprop.fset, method(func))

def makeProperty(name, default=None):
    protected = '_z_%s__' % name
    sys._getframe(1).f_locals[name] = property(
        lambda self: getattr(self, protected, default),
        method(lambda self, value: setattr(self, protected, value)))

def supercall(name):
    sys._getframe(1).f_locals[name] = method(
        lambda self, *args, **kwargs: getattr(
            super(self.__class__, self), name)(*args, **kwargs))

class Data(persistent.Persistent):
    interface.implements(interfaces.IData)
    def __init__(self):
        self._z__freeze_timestamp = datetime.datetime.now(pytz.utc)

    @property
    def _z_freeze_timestamp(self):
        return self._z__freeze_timestamp
    

class Freezing(object):
    interface.implements(interfaces.IFreezing)

    _z__freezing_data = None

    @property
    def _z_frozen(self):
        return self._z__freezing_data is not None

    @property
    def _z_freeze_timestamp(self):
        res = self._z__freezing_data
        if res is not None:
            return res._z_freeze_timestamp

    @method
    def _z_freeze(self):
        self._z__freezing_data = Data()
        event.notify(interfaces.ObjectFrozenEvent(self))

KEY = "zc.freeze._z_freeze_timestamp"

class FreezingAdapter(object):
    interface.implements(interfaces.IFreezing)
    component.adapts(zope.annotation.interfaces.IAnnotatable)

    def __init__(self, context):
        self.context = context

    @Lazy
    def annotations(self):
        return zope.annotation.interfaces.IAnnotations(self.context)

    @property
    def _z_frozen(self):
        return self.annotations.get(KEY) is not None

    @property
    def _z_freeze_timestamp(self):
        res = self.annotations.get(KEY)
        if res is not None:
            return res._z_freeze_timestamp

    @method
    def _z_freeze(self):
        self.annotations[KEY] = Data()
        event.notify(interfaces.ObjectFrozenEvent(self.context))

