#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import os
import re
import textwrap

from fnmatch import fnmatch
from ConfigParser import ConfigParser
from cli import platform


class enum(object):
    """A setting that can have one of a predetermined set of values."""

    def __init__(self, *values):
        self.values = values

    def __call__(self, value):
        if value not in self.values:
            raise ValueError
        return value


class regex(object):
    """A setting that is matched against a regular expression."""

    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __call__(self, value):
        if not self.regex.match(value):
            raise ValueError
        return value


class Settings(dict):
    """Base class for settings."""

    name = 'cli'
    validators = [
        ('ps1', str),
        ('ps2', str)
    ]
    defaults = {
        'ps1': '$ ',
        'ps2': '> '
    }
    example = textwrap.dedent("""
        [cli]
        #ps1 = %(ps1)s
        #ps2 = %(ps2)s
        """) % defaults

    def __init__(self, ignore_unknown=False, **kwargs):
        self.ignore_unknown = ignore_unknown
        self.update(self.defaults)
        if kwargs:
            self.update(kwargs)

    def __setitem__(self, key, value):
        for pattern,validator in self.validators:
            if not fnmatch(key, pattern):
                continue
            value = validator(value)
            super(Settings, self).__setitem__(key, value)
            return
        if not self.ignore_unknown:
            raise KeyError, 'unknown setting: %s' % key

    def load_config_file(self):
        """Load default values from a configuration file."""
        fname = platform.local_settings_file(self.name)
        if fname is None:
            return
        cp = ConfigParser()
        if not cp.read(fname):
            return
        if cp.has_section('main'):
            for key,value in cp.items('main'):
                self[key] = value

    def write_example_config_file(self):
        """Write an example config file."""
        if not self.example:
            return
        fname = platform.local_settings_file('rhev')
        if fname is None:
            return
        if os.access(fname, os.R_OK):
            return
        try:
            fout = file(fname, 'w')
            fout.write(self.example)
            fout.close()
        except IOError:
            pass
