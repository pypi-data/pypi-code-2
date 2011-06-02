"""The code in this module is mostly copy/pasted out of the distutils2 source
code, as recommended by Tarek Ziade.  As such, it may be subject to some change
as distutils2 development continues, and will have to be kept up to date.

I didn't want to use it directly from distutils2 itself, since I do not want it
to be an installation dependency for our packages yet--it is still too unstable
(the latest version on PyPI doesn't even install).
"""

import distutils.ccompiler
import os
import re
import sys

from setuptools.dist import Distribution
from setuptools.extension import Extension
try:
    from ConfigParser import RawConfigParser
except ImportError:
    from configparser import RawConfigParser


# A simplified RE for this; just checks that the line ends with version
# predicates in ()
_VERSION_SPEC_RE = re.compile(r'\s*(.*?)\s*\((.*)\)\s*$')


def resolve_name(name):
    """Resolve a name like ``module.object`` to an object and return it.

    Raise ImportError if the module or name is not found.
    """

    parts = name.split('.')
    cursor = len(parts)
    module_name = parts[:cursor]

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name))
            break
        except ImportError:
            if cursor == 0:
                raise
            cursor -= 1
            module_name = parts[:cursor]
            ret = ''

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError:
            raise ImportError(name)

    return ret



# TODO: This is getting pretty hefty; might want to break it up a bit
def cfg_to_args(path='setup.cfg'):
    """ Distutils2 to distutils1 compatibility util.

        This method uses an existing setup.cfg to generate a dictionary of
        keywords that can be used by distutils.core.setup(kwargs**).

        :param file:
            The setup.cfg path.
        :raises DistutilsFileError:
            When the setup.cfg file is not found.

    """
    # We need to declare the following constants here so that it's easier to
    # generate the setup.py afterwards, using inspect.getsource.

    # XXX ** == needs testing
    D1_D2_SETUP_ARGS = {"name": ("metadata",),
                        "version": ("metadata",),
                        "author": ("metadata",),
                        "author_email": ("metadata",),
                        "maintainer": ("metadata",),
                        "maintainer_email": ("metadata",),
                        "url": ("metadata", "home_page"),
                        "description": ("metadata", "summary"),
                        "long_description": ("metadata", "description"),
                        "download-url": ("metadata",),
                        "classifiers": ("metadata", "classifier"),
                        "platforms": ("metadata", "platform"),  # **
                        "license": ("metadata",),
                        # Use setuptools install_requires, not
                        # broken distutils requires
                        "install_requires": ("metadata", "requires_dist"),
                        "provides": ("metadata", "provides_dist"),  # **
                        "obsoletes": ("metadata", "obsoletes_dist"),  # **
                        "package_dir": ("files", 'packages_root'),
                        "packages": ("files",),
                        "package_data": ("files",),
                        "data_files": ("files",),
                        "scripts": ("files",),
                        "py_modules": ("files", "modules"),   # **
                        "cmdclass": ("global", "commands")
                        }

    MULTI_FIELDS = ("classifiers",
                    "platforms",
                    "install_requires",
                    "provides",
                    "obsoletes",
                    "packages",
                    "package_data",
                    "data_files",
                    "scripts",
                    "py_modules",
                    "cmdclass")

    # The method source code really starts here.
    parser = RawConfigParser()
    if not os.path.exists(path):
        raise DistutilsFileError("file '%s' does not exist" %
                                 os.path.abspath(path))
    parser.read(path)
    config = {}
    for section in parser.sections():
        config[section] = dict(parser.items(section))

    # Run setup_hook, if configured
    # TODO: We need a better way of displaying errors that occur in setup_hook;
    # right now they only show up as errors 'parsing' the cfg file.  A
    # traceback and other info would be nice...
    setup_hook = has_get_option(config, 'global', 'setup_hook')
    if setup_hook:
        hook = resolve_name(setup_hook)
        hook(config)

    register_custom_compilers(config)

    kwargs = {}

    for arg in D1_D2_SETUP_ARGS:
        if len(D1_D2_SETUP_ARGS[arg]) == 2:
            # The distutils field name is different than distutils2's.
            section, option = D1_D2_SETUP_ARGS[arg]

        elif len(D1_D2_SETUP_ARGS[arg]) == 1:
            # The distutils field name is the same thant distutils2's.
            section = D1_D2_SETUP_ARGS[arg][0]
            option = arg

        in_cfg_value = has_get_option(config, section, option)
        if not in_cfg_value:
            # There is no such option in the setup.cfg
            if arg == "long_description":
                in_cfg_value = has_get_option(config, section,
                                              "description-file")
                if in_cfg_value:
                    in_cfg_value = split_multiline_field(in_cfg_value)
                    value = ''
                    for filename in in_cfg_value:
                        description_file = open(filename)
                        try:
                            value += description_file.read().strip() + '\n\n'
                        finally:
                            description_file.close()
                    in_cfg_value = value
            else:
                continue

        if arg in MULTI_FIELDS:
            in_cfg_value = split_multiline_field(in_cfg_value)

        if in_cfg_value:
            if arg == 'install_requires':
                # Replaces PEP345-style version specs with the sort expected by
                # setuptools
                in_cfg_value = [_VERSION_SPEC_RE.sub(r'\1\2', pred)
                                for pred in in_cfg_value]
            elif arg == 'package_dir':
                in_cfg_value = {'': in_cfg_value}
            elif arg in ('package_data', 'data_files'):
                # The setup.cfg format currently only supports one glob per
                # package (or at least that's the way it's parsed).  This
                # should be fixed.  It also doesn't support '' for the package.
                data_files = {}
                for data in in_cfg_value:
                    data = data.split('=', 1)
                    if len(data) != 2:
                        continue
                    key, value = data[0].strip(), data[1].strip()
                    value = value.split()
                    data_files[key] = value
                if arg == 'data_files':
                    # the data_files value is a pointlessly different structure
                    # from the package_data value
                    data_files = data_files.items()
                in_cfg_value = data_files
            elif arg == 'cmdclass':
                cmdclass = {}
                dist = Distribution()
                for cls in in_cfg_value:
                    cls = resolve_name(cls)
                    cmd = cls(dist)
                    cmdclass[cmd.get_command_name()] = cls
                in_cfg_value = cmdclass

        kwargs[arg] = in_cfg_value


    kwargs['ext_modules'] = get_extension_modules(config)


    return kwargs



def register_custom_compilers(config):
    """Handle custom compilers; this has no real equivalent in distutils, where
    additional compilers could only be added programmatically, so we have to
    hack it in somehow.
    """

    compilers = has_get_option(config, 'global', 'compilers')
    if compilers:
        compilers = split_multiline_field(compilers)
        for compiler in compilers:
            compiler = resolve_name(compiler)

            # In distutils2 compilers these class attributes exist; for
            # distutils1 we just have to make something up
            if hasattr(compiler, 'name'):
                name = compiler.name
            else:
                name = compiler.__name__
            if hasattr(compiler, 'description'):
                desc = compiler.description
            else:
                desc = 'custom compiler %s' % name

            module_name = compiler.__module__
            # Note; this *will* override built in compilers with the same name
            # TODO: Maybe display a warning about this?
            cc = distutils.ccompiler.compiler_class
            cc[name] = (module_name, compiler.__name__, desc)

            # HACK!!!!  Distutils assumes all compiler modules are in the
            # distutils package
            sys.modules['distutils.' + module_name] = sys.modules[module_name]


def get_extension_modules(config):
    """Handle extension modules"""

    EXTENSION_FIELDS = ("sources",
                        "include_dirs",
                        "define_macros",
                        "undef_macros",
                        "library_dirs",
                        "libraries",
                        "runtime_library_dirs",
                        "extra_objects",
                        "extra_compile_args",
                        "extra_link_args",
                        "export_symbols",
                        "swig_opts",
                        "depends")

    ext_modules = []
    for section in config:
        labels = section.split('=')
        if (len(labels) == 2) and (labels[0] == 'extension'):
            ext_args = {}
            for field in EXTENSION_FIELDS:
                value = has_get_option(config, section, field)
                # All extension module options besides name can have multiple
                # values
                if not value:
                    continue
                value = split_multiline_field(value)
                if field == 'define_macros':
                    macros = []
                    for macro in value:
                        macro = macro.split('=', 1)
                        if len(macro) == 1:
                            macro = (macro[0].strip(), None)
                        else:
                            macro = (macro[0].strip(), macro[1].strip())
                        macros.append(macro)
                    value = macros
                ext_args[field] = value
            if ext_args:
                if 'name' not in ext_args:
                    ext_args['name'] = labels[1]
                ext_modules.append(Extension(ext_args.pop('name'),
                                             **ext_args))
    return ext_modules


def has_get_option(config, section, option):
    if section in config and option in config[section]:
        return config[section][option]
    elif section in config and option.replace('_', '-') in config[section]:
        return config[section][option.replace('_', '-')]
    else:
        return False


def split_multiline_field(value):
    # Special behaviour when we have a multi line option
    value = [v for v in
             [v.strip() for v in value.split('\n')]
             if v != '']
    return value


