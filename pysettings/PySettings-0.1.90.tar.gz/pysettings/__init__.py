# Copyright (c) 2010, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of this project nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


'''A simple settings management package for python.

Provides a configuration similar to that found in Django (e.g. load settings
from a Python module).

.. autosummary::
   :toctree: generated

   pysettings.loaders
   pysettings.modules

'''


import operator


class Settings(object):
    '''A collection of settings for an application.

    This object contains settings in a mutable, key-value way.

    Initialize the settings with key-value pairs.

    .. doctest::

       >>> s = Settings(FOO='hello', BAR='world', baz='lowercase too')
       >>> s.FOO
       'hello'
       >>> s.BAR
       'world'
       >>> s.baz
       'lowercase too'

    Dictionaries can be used too.

    .. doctest::

       >>> d = {'FOO':'hello', 'BAR':'world'}
       >>> e = {'baz':'lowercase too'}
       >>> s = Settings(d, e)
       >>> s.FOO
       'hello'
       >>> s.BAR
       'world'
       >>> s.baz
       'lowercase too'

    Mixing dictionaries and key-value pairs is OK too.  When mixing, the
    key-value pairs take precedence.

    .. doctest::

       >>> d = {'FOO':'hello', 'BAR':'world'}
       >>> s = Settings(d, BAR='earth', baz='lowercase too')
       >>> s.FOO
       'hello'
       >>> s.BAR
       'earth'
       >>> s.baz
       'lowercase too'
       >>> pprint(s._values)
       {'BAR': 'earth', 'FOO': 'hello', 'baz': 'lowercase too'}
       >>> s.quux
       Traceback (most recent call last):
       AttributeError: 'Settings' object has no attribute 'quux'

    Setting attributes works as well:

    .. doctest::

       >>> s = Settings()
       >>> s.A = 1
       >>> s.B = 2
       >>> s.C = 3
       >>> pprint(s._values)
       {'A': 1, 'B': 2, 'C': 3}

    Notice that key names may not start with an underscore.

    .. doctest::

       >>> s = Settings(_foo='invalid')
       Traceback (most recent call last):
       KeyError: "'Settings' keys may not begin with '_'."
       >>> s = Settings()
       >>> s._foo = 'invalid'
       Traceback (most recent call last):
       KeyError: "'Settings' keys may not begin with '_'."

    '''

    # pylint: disable-msg=R0903

    def __init__(self, *args, **kwargs):
        keys = reduce(operator.add, [a.keys() for a in args], [])
        keys += kwargs.keys()
        if len([k for k in keys if k.startswith('_')]) > 0:
            raise KeyError("'Settings' keys may not begin with '_'.")
        object.__setattr__(self, '_values', dict())
        for arg in args:
            self._values.update(arg)
        self._values.update(kwargs)

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        else:
            error = "'Settings' object has no attribute '%s'" % name
            raise AttributeError(error)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            raise KeyError("'Settings' keys may not begin with '_'.")
        else:
            self._values[name] = value


class SettingsProxy(object):
    '''Proxy calls to the installed object.

    An empty proxy will raise errors on access.

    .. doctest::

       >>> sp = SettingsProxy()
       >>> sp.configured
       False
       >>> sp.HELLO
       Traceback (most recent call last):
       RuntimeError: Settings have not been configured
       >>> sp.HELLO = 'world'
       Traceback (most recent call last):
       RuntimeError: Settings have not been configured

    When a settings object is installed, the calls to `__getattr__` and
    `__setattr__` will pass through.

       >>> sp.configure(Settings({'HELLO': 'world'}))
       >>> sp.configured
       True
       >>> sp.HELLO
       'world'
       >>> sp.HELLO = 'WORLD'
       >>> sp.HELLO
       'WORLD'

    Another settings object cannot be installed without overriding the first.

    .. doctest::

       >>> sp.configure(Settings({'goodbye': 'world'}))
       Traceback (most recent call last):
       RuntimeError: Settings have already been configured

       >>> sp.configure(Settings({'goodbye': 'world'}), override=True)
       >>> sp.configured
       True
       >>> sp.goodbye
       'world'

    '''

    def __init__(self):
        self._s = None

    def configure(self, s, override=False):
        '''Lazily proxy to `s`.
        '''
        if self._s is None or override:
            self._s = s
        else:
            raise RuntimeError(_('Settings have already been configured'))

    @property
    def configured(self):
        return self._s is not None

    def __getattr__(self, name):
        if self._s is None:
            raise RuntimeError(_('Settings have not been configured'))
        return getattr(self._s, name)

    def __setattr__(self, name, value):
        if name == '_s':
            object.__setattr__(self, '_s', value)
        elif self._s is None:
            raise RuntimeError(_('Settings have not been configured'))
        else:
            return setattr(self._s, name, value)


def cascading_settings(*args):
    '''Merge several :class:`Settings` objects, similar to `dict.update`.

    .. doctest::

       >>> x = Settings({'hello': 'world'})
       >>> y = Settings({'hello': 'fred'})
       >>> z = Settings({'goodbye': 'cruel world'})
       >>> s = cascading_settings(x, y, z)
       >>> s.hello
       'fred'
       >>> s.goodbye
       'cruel world'

    '''
    _values = {}
    for arg in args:
        # pylint: disable-msg=W0212
        _values.update(arg._values)
    return Settings(_values)


settings = SettingsProxy()
