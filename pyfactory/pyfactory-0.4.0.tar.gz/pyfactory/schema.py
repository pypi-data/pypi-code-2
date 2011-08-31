"""
This module contains the schema decorator. Users of PyFactory
should instead import :py:func:`schema` directly from
:py:mod:`pyfactory`.
"""

from functools import wraps

def schema(model=None):
    """
    Decorator to mark a method in a :py:class:`Factory` as a schema.
    This decorator has no effect on functions which aren't part of a
    subclass of :py:class:`Factory`.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        # Mark this method as a factory
        wrapped._pyfactory = True

        return wrapped

    return decorator
