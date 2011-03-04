"""Configuration"""

import sys
from paste.deploy.loadwsgi import NicerConfigParser
import os

def listify_param(txt):
    result = []
    for line in txt.splitlines():
        if line and not line.isspace():
            result.append(line.strip())
    return result

def listify_param_pairs(txt):
    result = []
    for line in listify_param(txt):
        key, value = line.split()
        result.append((key, value))
    return result

def get_filepath_path(inifile, txt, error_info='', modules=sys.modules):
    if not ':' in txt:
        # use the directory of the inifile
        from_dir, dir = os.path.dirname(inifile), txt
    else:
        prefix = 'egg:'
        if not txt.startswith(prefix):
            raise ValueError, \
                'Tree path must contain a filepath, or start with `egg:` (%s) %s' % (
                    txt, error_info)
        txt_part = txt[len(prefix):]
        try:
            egg, dir = txt_part.split('/', 1)
        except ValueError:
            egg, dir = txt_part, ''
        # find the directory of the egg
        try:
            modules[egg]
        except KeyError:
            __import__(egg)
        egg_module = modules[egg]
        from_dir = os.path.dirname(egg_module.__file__)
    if dir:
        tree_path = os.path.join(from_dir, dir)
    else:
        tree_path = from_dir
    return tree_path

def get_ini_section(old_inifile, extension, error_info='', modules=sys.modules):
    if not ':' in extension:
        new_inifile, new_extension = old_inifile, extension
    else:
        prefix, extension_part = extension.split(':', 1)
        if prefix not in ('config', 'egg'):
            raise ValueError, \
                'extend_resources must contain a single ini file section, or start with `config:` or with `egg:`(%s) %s' % (
                    extension, error_info)
        try:
            new_inifile, new_extension = extension_part.split('#')
        except ValueError:
           raise ValueError, \
               'extend_resources must be in `config:/path/to/ini/file#section` format (%s) %s' % (
                extension, error_info)
        if prefix == 'config':
            # take new file path relative from the old inifile locations
            new_inifile = os.path.join(os.path.dirname(old_inifile), new_inifile)
        else:   # egg:
            try:
                egg, dir = new_inifile.split('/', 1)
            except ValueError:
                raise ValueError, \
                    'extend_resources must be in `egg:my.package/path/to/ini/file#section` format (%s) %s' % (
                    extension, error_info)
            # find the directory of the egg
            try:
                modules[egg]
            except KeyError:
                __import__(egg)
            egg_module = modules[egg]
            from_dir = os.path.dirname(egg_module.__file__)
            new_inifile = os.path.join(from_dir, dir)
    return new_inifile, new_extension

class JuicerConfigParser(NicerConfigParser):

    def load(self):
        """Loads the configuration file"""
        filename = self.filename.strip()
        defaults = dict(
            here = os.path.dirname(os.path.abspath(filename)),
            __file__ = os.path.abspath(filename),
            )
        # Stupid ConfigParser ignores files that aren't found, so
        # we have to add an extra check:
        if not os.path.exists(filename):
            raise IOError(
                "File %r not found" % filename)
        # Read the configuration and apply the defaults
        r = self.read(filename)
        for key, value in defaults.iteritems():
            self._defaults.setdefault(key, value)
        # Update the defaults with their interpolated values
        defaults = self.defaults()
        for key, value in defaults.iteritems():
            self._defaults[key] = value

    def get_section(self, section_name):
        new_config = self.items(section_name)
        # We don't want anything that is in the defaults, or is in our list of options
        # this makes it possible to check for extra values in a sensible way
        real_keys = set(self._sections[section_name].iterkeys())
        real_keys.update(('url_prefix', 'filepath'))
        real_keys.discard('__name__')
        result = [(k, v) for (k, v) in new_config if k in real_keys]
        return dict(result)
