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
        if key.startswith('__') and key.endswith('__'):
            return super(Options, self).__getattr__(key)
        return self._getFQ(key, None)

    def __setattr__(self, key, value):
        self._setFQ(key, value)

    def __getitem__(self, key):
        return self._getFQ(key, raise_exc=True)

    def __contains__(self, key):
        if '.' not in key:
            return super(Options, self).__contains__(key)
        (container, name, value) = self._getFQ_helper(key, raise_exc=False)
        assert isinstance(container, Options)
        return container.has_key(name)

    def has_key(self, key):
        if '.' not in key:
            return super(Options, self).has_key(key)
        (container, name, value) = self._getFQ_helper(key, raise_exc=False)
        assert isinstance(container, Options)
        return container.has_key(name)

    def _getFQ_helper(self, key, default=None, raise_exc=False):
        """
        Return a tuple (container, simple-name, value) for the given `key`.
        If the `key` is 'abc.def.xyz', and 'abc.def' is not found, then an Options
        instance for 'abc.def' is added if `raise_exc` is False, otherwise
        an exception is raised.
        If the `key` is 'abc.def.xyz' and 'xyz' is not found in 'abc.def', then
        `default` is returned if `raise_exc` is False, otherwise an exception
        is raised.
        """
        def make_name(prefix, postfix):
            if not prefix:
                return postfix
            return "%s.%s" % (prefix, postfix)
        d      = self
        d_name = ''
        name   = key
        while '.' in name:
            (prefix, postfix) = name.split('.', 1)
            prefix_v = d.get(prefix, None)
            if prefix_v is None:
                if raise_exc:
                    raise KeyError(make_name(d_name, prefix))
                prefix_v = Options()
                d[prefix] = prefix_v
            assert prefix_v is not None
            d      = prefix_v
            d_name = make_name(d_name, prefix)
            name   = postfix
        assert '.' not in name
        if not d.has_key(name):
            if raise_exc:
                raise KeyError(make_name(d_name, name))
            return (d, name, default)
        return (d, name, d.get(name, default))

    def _getFQ(self, key, default=None, raise_exc=False):
        """
        Return the value for the given `key`.
        If the `key` is 'abc.def.xyz', and 'abc.def' is not found, then an Options
        instance for 'abc.def' is added if `raise_exc` is False, otherwise
        an exception is raised.
        If the `key` is 'abc.def.xyz' and 'xyz' is not found in 'abc.def', then
        `default` is returned if `raise_exc` is False, otherwise an exception
        is raised.
        """
        (container, name, value) = self._getFQ_helper(key, default=default, raise_exc=False)
        assert isinstance(container, Options)
        if raise_exc and (not container.has_key(name)):
            raise KeyError(key)
        return value

    def _setFQ(self, key, value, raise_exc=False):
        """
        Set the value for the given `key`.
        If the `key` is 'abc.def.xyz', and 'abc.def' is not found, then an Options
        instance for 'abc.def' is added if `raise_exc` is False, otherwise
        an exception is raised.
        """
        (container, name, prev_value) = self._getFQ_helper(key, raise_exc=False)
        assert isinstance(container, Options)
        container[name] = value
        return prev_value

    def __call__(self, **kwargs):
        self.update(kwargs)
        return self

    def __hash__(self):
        return id(self)

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
                      dry_run = False,
                      ignore_errors = False
                      )
    return options

_setup_default_options()

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
