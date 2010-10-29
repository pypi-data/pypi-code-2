
__all__ = ['Component', "SharedComponent"]

from pyutilib.component.core import Plugin, implements
from plugin import IModelComponent


class Component(Plugin):

    implements(IModelComponent)

    def __init__ ( self, ctype=None, **kwargs ):
        if kwargs.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

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


class SharedComponent(object):
    """
    Component to be shared between Model objects.

    As the name implies, these Component objects are designed to allow
    multiple Model instances to share a set of common components to
    save memory. SharedComponent objects should only respond to a
    construction call once.

    Developer's note: SharedComponent does very little on its own. In
    fact all it does is override __deepcopy__ to return itself. For
    this reason it is very important that when you define classes that
    multiply inherit from SharedComponent and another class derived
    from Component, SharedComponent must come first in the list of
    base classes to ensure that SharedComponent.__deepcopy__ comes
    before the other overridden __deepcopy__ methods in the method
    resolution order.

    Example:
    ------------------------------------------------------------------

    # Correct
    class Foo(SharedComponent, Param):
        pass

    # Incorrect
    class Foo(Param, SharedComponent):
        pass

    ------------------------------------------------------------------

    In the incorrect case, Foo.__deepcopy__ references
    Param.__deepcopy__, which will perform an actual deep copy.

    Note that this ordering is safe, since SharedComponent defines no
    other methods besides those which it inherits.

    """

    def __deepcopy__(self, memo={}):
        """
        Sharing is implemented by transparently returning a reference
        to the same object when asked to copy itself.

        """
        return self


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
