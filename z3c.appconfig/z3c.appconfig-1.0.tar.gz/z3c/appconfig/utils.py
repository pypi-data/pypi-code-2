
def asBool(value):
    """Simple method to convert a string to a boolean.

    Accepted values for True are ``true``, ``yes`` and ``on``. The strings
    ``false``, ``no`` and ``off`` are converted to False. For non-string values
    the standard python boolean conversion is done.
    """
    if not isinstance(value, basestring):
        return bool(value)

    value=value.strip().lower()
    if value in [ "true", "yes", "on" ]:
        return True
    elif value in [ "false", "no", "off" ]:
        return False
    else:
        raise ValueError("Invalid boolean: %s" % value)


