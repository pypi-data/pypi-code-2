VERSION = (0, 3, 2)
 
def get_version():
    if len(VERSION) == 3:
        try:
            int(VERSION[2])
            v  = '%s.%s.%s' % VERSION
        except:
            v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v
 
__version__ = get_version()

from exceptions import *
