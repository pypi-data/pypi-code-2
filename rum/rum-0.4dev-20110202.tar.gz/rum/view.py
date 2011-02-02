from inspect import getargspec
from itertools import count

from peak.util.decorators import decorate_class

from rum.genericfunctions import generic, when
from rum.basefactory import BaseFactory

__all__ = ["ViewFactory"]


class ViewFactory(BaseFactory):
    """
    ViewFactory instances return initialized views when called.

    All the magic is done in :meth:`get` which is an abstract
    :func:`rum.genericfunctions.generic` function that subclasses
    extend to implement a pseudo-visitor pattern over objects and their
    attributes.
    """
    # These are used to auto-generate view ids in case they're not defined.
    id_prefix = 'rum'
    _serial = count(0)

    @generic
    def get(self, resource, parent=None, remote_name=None, attr=None,
            action=None, args=None):
        """
        Return a class implementing :class:`rum.interfaces.IView`.
        Depending on the action it should return a class implementing
        :class:`rum.interfaces.IInputView` instead.
        """

    def next_id(self):
        """
        Get a new unique id for the view

        Example::

            >>> f = ViewFactory()
            >>> f.id_prefix in f.next_id()
            True
        """
        return self.id_prefix + str(self._serial.next())

    # Placeholder for expected missing values
    class Missing(object): pass


    @classmethod
    def view(cls, *args, **kw):
        import warnings
        warnings.warn(
            "view() is deprecated. Please use register() instead",
            DeprecationWarning, 2
            )
        def do_register(resource):
            names = getargspec(cls.get)[0][2:]
            conds = {}
            for n in names:
                if n in kw:
                    conds[n] = kw.pop(n)
            cls.register(view, resource, defaults=kw, **conds)
            return resource
        if len(args) == 1:
            # being called as class decorator to register a whole view
            view = args[0]
            return decorate_class(do_register)
        elif len(args) == 2:
            # being called mapper-style to register a whole view
            resource, view = args
            return do_register(resource)
        else:
            raise TypeError(
                cls.__name__+'.view cannot be called with those arguments'
                )

    @get.when("action=='delete'", prio=-10)
    def _dummy_delete_form(self, *args, **kw):
        return _DummyDeleter()

class _DummyDeleter(object):
    def validate(self, obj, state=None):
        return obj
