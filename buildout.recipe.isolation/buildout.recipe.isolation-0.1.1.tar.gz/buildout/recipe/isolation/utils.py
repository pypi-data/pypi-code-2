# -*- coding: utf-8 -*-

def as_bool(value):
    """Parse a value for it's boolean equivalent."""
    if value is None:
        value = False
    elif isinstance(value, bool) or isinstance(value, int):
        pass
    elif isinstance(value, str):
        value = value.lower()
        if value == 'true':
            value = True
        else:
            value = False
    else:
        raise TypeError("Could not determine the boolean value of " \
            "%s." % value)
    return value
