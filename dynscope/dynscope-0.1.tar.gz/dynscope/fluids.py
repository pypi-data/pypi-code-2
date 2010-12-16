"""
This module implements simple dynamically scoped namespaces for python. Those
namespaces are objects with an associated context manager to have scoped
stacking of dynamic environments with dynamically scoped shadowing of values in
outer layers.

The outer dynscope module provides a global dynamic namespace fluid with it's
associated manager flet and a constructor function construct that allows
construction of isolated dynamic namespaces.

This module contains the implementations of dynamic environments and dynamic
scopes.
"""
import threading

class DynamicEnvironment(threading.local):
    """
    This class implements the dynamic environment on top of the threading.local
    class. Additionally to the basic functionality of threading.local it
    provides stacking of environments with lookup of variables in the layered
    environment. Dynamic variables keep their layer unless they are shadowed by
    new bindings even on assignment.

    This means that if you want to shadow a global variable, you have to
    explicitely localize it in the new subenvironment.

    Dynamic variables are kept in the environments __dict__, so even on direct
    introspection a dynamic environment will behave like a normal object.
    """

    def __init__(self, parent=None):
        """
        Initialize a new environment that can be linked to a parent
        environment.
        """
        self._parent = parent

    def _update(self, items):
        """
        Load a whole dict of variables into the environment.  Variables
        starting with _ are not allowed to prevent overloading internal
        variables.
        """
        keys = [k for k in items.iterkeys() if not k.startswith('_')]
        if len(keys) != len(items):
            raise ValueError("dynamic variables must not start with an underscore")
        self.__dict__.update((k,items[k]) for k in keys)

    def _find_env(self, attr):
        """
        Returns the environment that carries the given attribute or raises
        AttributeError if it can't be found.
        """
        if attr in self.__dict__:
            return self
        if self._parent:
            return self._parent._find_env(attr)
        raise AttributeError(attr)

    def __getattr__(self, attr):
        """
        Handle attributes starting with _ locally, everything else is sent into
        the dynamic environment.
        """
        if attr.startswith('_'):
            return super(DynamicEnvironment, self).__getattr__(attr)
        else:
            env = self._find_env(attr)
            return env.__dict__[attr]

    def __setattr__(self, attr, value):
        """
        Handle attributes starting with _ locally, everything else is sent into
        the dynamic environment. Variables that not yet exist are created in
        the outmost layer.
        """
        if attr.startswith('_'):
            return super(DynamicEnvironment, self).__setattr__(attr, value)
        else:
            try:
                env = self._find_env(attr)
            except AttributeError:
                env = self
            env.__dict__[attr] = value

class DynamicScope(object):
    """
    This class encapsulates the dynamic scope. The scope just manages one
    environment, which can be stacked. The scope provides the function to do
    the actual stacking, the unwinding is handled by a local class of that
    function.

    Attribute access is delegated to the environment for attributes that don't
    start with an underscore.
    """

    @classmethod
    def _construct(cls):
        """
        Constructor that returns the fluid and flet pair for a dynamic scope
        manager.
        """
        o = cls()
        return o, o._flet

    def __init__(self):
        self._env = DynamicEnvironment()

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return super(DynamicScope, self).__getattr__(attr)
        else:
            return getattr(self._env, attr)

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            return super(DynamicScope, self).__setattr__(attr, value)
        else:
            setattr(self._env, attr, value)

    def _flet(self, **kw):
        """
        This function handles the actual stacking of scopes. It returns a
        context manager that handles the unwinding. To protect the dynamic
        scope, the context manager is a local class instance that captures
        the active dynamic scope in a closure.
        """

        class DynamicScopeUnwindProtect(object):
            def __enter__(this):
                self._env = DynamicEnvironment(self._env)
                self._env._update(kw)
                return this
            def __exit__(this, *args):
                self._env = self._env._parent
                return False

        return DynamicScopeUnwindProtect()

