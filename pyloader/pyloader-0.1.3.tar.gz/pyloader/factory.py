#!/usr/bin/env python

"""
abstract factories
"""

import cast
import loader
import os
import sys
from copy import deepcopy
from optparse import OptionParser
from ConfigParser import InterpolationDepthError
from ConfigParser import InterpolationMissingOptionError
from ConfigParser import InterpolationSyntaxError
from ConfigParser import SafeConfigParser as ConfigParser

__all__ = ['CircularReferenceError', 'PyFactory', 'IniFactory']

class CircularReferenceError(Exception):
    """factory has detected a circular reference"""

class PyFactory(object):

    # to evaluate arguments as objects 
    delimeters = ('%(', ')s')

    def __init__(self, config=None, main=''):
        self.main = main  # main section
        self.configure(config or {})

    def configure(self, config):
        """load a new configuration"""
        # TODO: this should really be a configuration update.  If you keep
        # track of all "apps" and their parents (i.e. as a ADG)
        # you should be able to update only relevent apps
        self.config = config
        self.seen = set() # already seen apps to note cyclic dependencies
        self.parsed = {}  # instantiated apps

    def load(self, name=None):
        """load an object"""
        
        name = name or self.main # load main section by default
        assert name in self.config, "'%s' not found in configuration"
        if name in self.parsed:
            return self.parsed[name]
        if name in self.seen:
            raise CircularReferenceError('Circular reference! : %s' % name)
        self.seen.add(name)

        # get section
        section = self.config[name]
        assert 'path' in section

        # load object
        obj = loader.load(section['path'])

        # get the object's arguments (if any)
        args = section.get('args', None)
        kwargs = section.get('kwargs', None)

        # if args and kwargs aren't there, you're done!
        if args is None and kwargs is None:
            self.parsed[name] = obj
            return obj

        # interpolate arguments
        if args:
            args = [self.interpolate(arg) for arg in args]
        else:
            args = []
        if kwargs:
            kwargs = dict([(key, self.interpolate(value))
                           for key, value in kwargs.items()])
        else:
            kwargs = {}

        # invoke
        self.parsed[name] = obj(*args, **kwargs)
        return self.parsed[name]

    def interpolate(self, value):

        # only interpolate strings
        if not isinstance(value, basestring):
            return value

        if value.startswith(self.delimeters[0]) and value.endswith(self.delimeters[1]):
            value = value[len(self.delimeters[0]):-len(self.delimeters[1])]
            if value in self.config:
                return self.load(value)
        return value
                                                            
class IniFactory(PyFactory):
    """load a python object from an .ini file"""

    def __init__(self, inifile, main=''):
        assert os.path.exists(inifile), "File not found: %s" % inifile
        self.inifile = inifile
        config = self.read(inifile)
        PyFactory.__init__(self, config, main)

    @classmethod
    def configuration(cls, iniconfig, **defaults):
        """interpret configuration from raw .ini syntax"""
        config = {}
        interpolated = set()
        seen = set()
        object_string = '%(object)s'

        # create a hash of section names
        names = {}
        for section in iniconfig:

            # sanity check
            assert ':' in section, "No : in section: %s" % section

            name = section.split(':',1)[0]
            names[name] = section

        def create_section(section, options):

            # split up the section identifier
            name, path = section.split(':', 1)

            # make a dict for the section
            sect = {}

            # interpret decorators
            if ':' in path:
                wrapper, _path = path.split(':', 1)
                # TODO: could interpolate wrapper 
                if wrapper in names:

                    # inline wrapper arguments:
                    # [extended-fibonacci:@:four=4,five=5:fibonacci]
                    _wrapper_args = None
                    _wrapper_kwargs = None
                    if ':' in _path:
                        _wrapper_options, __path = _path.split(':', 1)
                        if ',' in _wrapper_options or '=' in _wrapper_options:
                            # ,= : tokens to ensure these are wrapper options
                            # as these shouldn't be found in a real path (dotted path or file path)
                            _wrapper_args, _wrapper_kwargs = cast.str2args(_wrapper_options)
                            _path = __path

                    if _path in names:
                        # [foo:bar:fleem]
                        wrapped_name = _path
                    else:
                        # stub value for "anonymous" name
                        # [foo:bar:%(here)s/objects.py:MyClass]
                        wrapped_name = section

                    # get wrapper options
                    if wrapper not in config:
                        # load wrapper configuration 
                        wrapper_section = names[wrapper]
                        if wrapper_section in seen:
                            pass # TODO
                        create_section(wrapper_section, iniconfig[wrapper_section])
                    wrapper_options = deepcopy(config[wrapper])

                    # add inline wrapper args, kwargs
                    if _wrapper_args is not None:
                        if 'args' in wrapper_options:
                            wrapper_options['args'].extend(_wrapper_args)
                        else:
                            wrapper_options['args'] = _wrapper_args
                    if _wrapper_kwargs is not None:
                        if 'kwargs' in wrapper_options:
                            wrapper_options['kwargs'].update(_wrapper_kwargs)
                        else:
                            wrapper_options['kwargs'] = _wrapper_kwargs

                    # interpolate wrapper_options
                    def interpolate(option):
                        if option == object_string:
                            return '%(' + wrapped_name + ')s'
                        return option
                    if 'args' in wrapper_options:
                        args = wrapper_options['args'][:]
                        args = [interpolate(i) for i in args]
                        wrapper_options['args'] = args
                    if 'kwargs' in wrapper_options:
                        kwargs = wrapper_options['kwargs'].copy()
                        kwargs = dict([(i,interpolate(j)) for i, j in kwargs.items()])
                        wrapper_options['kwargs'] = kwargs

                    # create wrapper
                    config[name] = wrapper_options
                    if _path == wrapped_name:
                        return
                    name = wrapped_name
                    path = _path

            elif path in names:
                # override section: [foo:bar]
                if path not in config:
                    # load overridden section
                    overridden_section = names[path]
                    if overridden_section in seen:
                        pass # TODO
                    create_section(overridden_section, iniconfig[overridden_section])
                sect = deepcopy(config[path])

            if 'path' not in sect:
                # add the path to section dict
                path = path % defaults
                sect['path'] = path

            # get arguments from .ini options
            for option, value in options.items():
                if option == '.': # positional arguments
                    sect['args'] = cast.str2list(value)
                else: # keyword arguments
                    sect.setdefault('kwargs', {})[option] = value

            # set the configuration
            config[name] = sect

        # get the object definitions
        for section, options in iniconfig.items():
            seen.add(section)
            if section not in interpolated:
                create_section(section, options)
            interpolated.add(section)
                    
        return config
        
    @classmethod
    def read(cls, inifile):
        """reads configuration from an .ini file"""

        here = os.path.dirname(os.path.abspath(inifile))
        
        # read configuration
        defaults={'here': here,
                  'this': os.path.abspath(inifile)}
        parser = ConfigParser(defaults=defaults)
        parser.optionxform = str # use whole case
        parser.read(inifile)

        # parse configuration
        config = {}
        for section in parser.sections():

            config[section] = {}

            # read the options
            for option in parser.options(section):

                if option in parser.defaults():
                    # don't include the defaults
                    continue

                # try to interpolate the option
                # otherwise, use the raw value
                try:
                    value = parser.get(section, option)
                except (InterpolationMissingOptionError, InterpolationSyntaxError, InterpolationDepthError):
                    value = parser.get(section, option, raw=True)

                config[section][option] = value

        return cls.configuration(config, **parser.defaults())

def main(args=sys.argv[1:]):
    """command line entry point"""
    usage = '%prog file1.ini -arg1 -arg2 --key1=value1 --key2=value2'
    parser = OptionParser(usage=usage, description=IniFactory.__doc__)
    options, args = parser.parse_args(args)

    if len(args) != 1:
        parser.print_usage()
        parser.exit()

    factory = IniFactory(args[0])
    obj = factory.load()
    print obj

if __name__ == '__main__':
    main()
