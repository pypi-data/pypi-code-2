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
        raise TypeError("Could not determine the boolean value of "
            "%s." % value)
    return value

def as_list(value):
    """Parse a value for it's list equivalent."""
    if value is None:
        value = []
    elif isinstance(value, list) or isinstance(value, tuple):
        pass
    elif isinstance(value, str):
        value = [ v for v in value.split('\n') if v ]
    else:
        raise TypeError("Could not parse the list value of %s." % value)
    return value

def as_string(value):
    """Parse a value for it's equivalent string reprsentation."""
    if value is None:
        value = ''
    elif isinstance(value, str) or isinstance(value, int):
        value = str(value)
    elif isinstance(value, list) or isinstance(value, tuple):
        numb = []
        if len(value) > 1:
            numb = ['']
        value = '\n'.join(numb + value)
    elif isinstance(value, bool):
        if value:
            value = 'true'
        else:
            value = 'false'
    else:
        raise TypeError("Could not transform the value %s into a string."
                        % value)
    return value
