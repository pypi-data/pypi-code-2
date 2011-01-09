import os

import decorator

def catching(exception_type=Exception, handler=None):
    def catching(f, *args, **kw):
        try:
            return f(*args, **kw)
        except exception_type as e:
            if handler:
                handler(e)

    return decorator.decorator(catching)

def fullpath(path):
    return os.path.abspath(
        os.path.expanduser(path))
