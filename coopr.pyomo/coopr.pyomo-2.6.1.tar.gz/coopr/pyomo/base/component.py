
__all__ = ['Component']

from pyutilib.component.core import Plugin, implements
from plugin import IModelComponent


class Component(Plugin):

    implements(IModelComponent)

    def __init__ ( self, ctype=None, **kwargs ):
        # Error check for ctype
        if ctype is None:
            raise DeveloperError, "Must specify a class for the component type!"

        self.active=True
        self._type=ctype
        self._constructed=False
        self.model=None

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def type(self):
        return self._type

    def construct(self, data=None):
        pass

    def is_constructed(self):
       return self._constructed


class DeveloperError(Exception):
    """
    Exception class used to throw errors stemming from Pyomo
    programming errors, rather than user modeling errors (e.g., a
    component not declaring a 'ctype')

    """

    def __init__(self, val):
        self.parameter = val

    def __str__(self):
        return repr(self.parameter)
