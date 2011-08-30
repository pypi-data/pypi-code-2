"""
Contains the schema decorator.
"""

from functools import wraps

def schema(model=None):
    """
    Decorator to mark a method as a schema for a factory.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        # Mark this method as a factory
        wrapped._pyfactory = True

        return wrapped

    return decorator
