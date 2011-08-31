"""
Contains the exceptions that can be raised by PyFactory.
"""

class InvalidModelBuilderError(Exception):
    """
    This exception is raised when a model builder doesn't properly
    implement a method that it should have, when it is needed.

    For example, the `getattr` method on model builders isn't strictly
    required unless an association is used with that model. In that
    case, if `getattr` isn't implemented, then this exception would
    be raised.
    """
    pass
