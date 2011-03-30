# -*- coding: utf-8 -*-

options = None

class Options(dict):
    """
    An extended dictionary, allowing access to keys also as instance attributes.

       >>> d = Options()

       >>> d['k1'] = 23

       >>> d['k1']
       23

       >>> d.k1
       23

       >>> d.var = 'hello'

       >>> d['var']
       'hello'

       >>> d.var
       'hello'

       >>> d = Options(initval = 5)
       >>> d.initval
       5
    """

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value

    def _getFQ(self, key):
        d = self
        while '.' in key:
            (prefix, postfix) = key.split('.', 1)
            v = d.get(prefix, None)
            if v is None:
                return None
            d = v
            key = postfix
        return d.get(key, None)

    def __call__(self, **kwargs):
        self.update(kwargs)
        return self

def _setup_default_options():
    global options

    import sys
    import platform

    if options is not None:
        return options

    vtuple = platform.python_version_tuple()
    options = Options(sys = Options(executable          = sys.executable,
                                    prefix              = sys.prefix,
                                    platform            = sys.platform,
                                    machine             = platform.machine(),
                                    system              = platform.system(),
                                    python_version      = vtuple,
                                    python_version_tag  = '%s.%s' % (vtuple[0], vtuple[1]),
                                    python_version_info = sys.version_info,
                                    lib_build_ver       = '%s-%s' % (platform.system().lower(), platform.machine())),
                      dry_run = False
                      )
    return options

_setup_default_options()

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
