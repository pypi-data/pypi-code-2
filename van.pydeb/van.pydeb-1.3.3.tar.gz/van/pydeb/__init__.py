##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import sys
import os.path
import optparse
import logging

from pkg_resources import PathMetadata, Distribution
from pkg_resources import component_re # Is this a public interface?

_HERE = os.path.dirname(__file__)

logger = logging.getLogger('van.pydeb')

#
# Command Line Interface
#

_COMMANDS = {}

def main(argv=sys.argv):
    # Setup logging early
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    # Handle global options and dispatch the command 
    assert len(argv) >= 2, "You need to specify a command"
    command = _COMMANDS.get(argv[1])
    if command is None:
        raise Exception("No Command: %s" % argv[1])
    return command(argv)

#
# Package name conversion
#

# An attempt at a cannonical list of translations
def _read_map(file):
    map = {}
    reverse_map = {}
    try:
        f = open(file, 'r')
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            items = line.split()
            items.append('')
            k, v, options = items[:3]
            options = options.split(',')
            optdict = {}
            for option in options:
                if not option:
                    continue
                if '=' in option:
                    option, value = option.split('=')
                if option in set(['reduced']):
                    optdict[option] = value
                    continue
                raise Exception("Unknown option %s" % option)
            assert k not in map, "Duplicate key %s already in map. File %s" % (k, file)
            map[k] = (v, optdict)
            assert v not in reverse_map, "Duplicate key %s already in reverse map. File %s" % (v, file)
            reverse_map[v] = (k, optdict)
    finally:
        f.close()
    return map, reverse_map

_PY_TO_BIN, _BIN_TO_PY = _read_map(os.path.join(_HERE, 'py_to_bin.txt'))
_PY_TO_SRC, _SRC_TO_PY = _read_map(os.path.join(_HERE, 'py_to_src.txt'))

def _parse_override_bdep(parser):
    parser.add_option("--override-bdep", dest="override_bdep", action="append",
                      help="Override a binary-python dependency relation. Format: 'python_package_name binary_package_name'. Can be used multiple times.")

def _handle_override_bdep(options):
    if options.override_bdep is None:
        return
    for override in options.override_bdep:
        py, bin = override.split()
        _PY_TO_BIN[py] = (bin, {})
        _BIN_TO_PY[bin] = (py, {})

_DEFVAL = (None, None)

def py_to_bin(setuptools_project):
    """Convert a setuptools project name to a debian binary package name"""
    bin, options = _PY_TO_BIN.get(setuptools_project, _DEFVAL)
    if bin is None:
        return py_to_bin_default(setuptools_project)
    if 'reduced' in options:
        logger.info("Using %(bin)s as a dependency for %(st)s rather than %(full)s. This works in most cases, if not for you, adjust by hand", {'bin': bin, 'full': options['reduced'], 'st': setuptools_project})
    return bin

def py_to_bin_default(setuptools_project):
    """Convert a setuptools project name to a debian binary package name.
    
    This function is the fallback and represents the "default" naming schema.
    """
    name = setuptools_project.lower()
    if name.startswith('python-'):
        return name
    return 'python-%s' % name

def py_to_src(setuptools_project):
    """Convert a setuptools project name to a debian source package name"""
    return _PY_TO_SRC.get(setuptools_project, _DEFVAL)[0] or py_to_src_default(setuptools_project)

def py_to_src_default(setuptools_project):
    """Convert a setuptools project name to a debian source package name"""
    return setuptools_project.lower()

def bin_to_py(binary_package):
    """Convert a doebian binary package name to a setuptools project name"""
    # try for an exact match
    py_package_name = _BIN_TO_PY.get(binary_package, _DEFVAL)[0]
    if py_package_name is not None:
        return py_package_name
    # now we try guess
    return bin_to_py_default(binary_package)

def bin_to_py_default(binary_package):
    if binary_package.startswith('python-'):
        return binary_package[7:]
    return binary_package

def src_to_py(source_package):
    """Convert a debian source package name to a setuptools project name"""
    return _SRC_TO_PY.get(source_package, _DEFVAL)[0] or src_to_py_default(source_package)

def src_to_py_default(source_package):
    return source_package

def _string_command(argv):
    command = argv[1]
    parser = optparse.OptionParser(usage="usage: %%prog %s argument" % command)
    _parse_override_bdep(parser)
    options, args = parser.parse_args(argv)
    _handle_override_bdep(options)
    assert len(args) == 3, "Too many or few arguments %s" % args
    print {'py_to_src': py_to_src,
           'py_to_bin': py_to_bin,
           'bin_to_py': bin_to_py,
           'src_to_py': src_to_py,
           'py_version_to_deb': py_version_to_deb}[command](args[2])
    return 0
_COMMANDS['py_to_src'] = _COMMANDS['py_to_bin'] = _string_command
_COMMANDS['src_to_py'] = _COMMANDS['bin_to_py'] = _string_command
_COMMANDS['py_version_to_deb'] = _string_command

#
# Version Conversion
#


def py_version_to_deb(version):
    """Converts an egg version to debian format to preserve sorting rules.

    We try to convert egg versions to debian versions here in a way that
    preserves sorting rules and takes into account egg ideosynchracies. We also
    try to maintain readability of the version numbers and so do not aim for
    perfection (It's highly doubtful we could attain it anyway).

    For a simple and nasty example:

        >>> py_version_to_deb('2.8.0')
        '2.8.0'
        >>> py_version_to_deb('2.8.0pre1')
        '2.8.0~c~pre1'

    """
    version = version.lower()
    result = []
    for part in component_re.split(version):
        if not part or part.isdigit() or part == '.' or part == '-':
            result.append(part)
            continue
        result.append('~')
        if part in ['pre', 'preview', 'rc']:
            # ok. so because of the way setuptools does this, we can't manage to preserve the original
            # version number and maintain sort order
            result.append('c~')
        if part == 'dev':
            result.append('~')
        result.append(part)
    return ''.join(result)

#
# Dependency Conversion
#

_setuptools_debian_operators = {'>=': '>=',
                                '>': '>>',
                                '<': '<<',
                                '==': '=',
                                '!=': None, # != not supported by debian, use conflicts in future for this
                                '<=': '<='}

def _depends_or_provides(argv):
    """Run the dependency calculation program.

        >>> import os
        >>> here = os.path.dirname(__file__)
        >>> ex1 = os.path.join(here, 'tests', 'dummy.foo.egg-info')
        >>> exitcode = main(['bin', 'depends', '--egg-info', ex1])
        python-bar (<< 0.3~c~pre1), python-dummy, python-foo (>> 0.1), python-foobar
        >>> exitcode
        0
    """
    parser = optparse.OptionParser(usage="usage: %prog command [options]")
    parser.add_option("--egg-info", dest="egg_info",
                      help="The egg-info directory to use.")
    parser.add_option("--exclude-extra", dest="exclude_extras", action="append",
                      help="Exclude extras from dependencies")
    parser.add_option("--extra", dest="extras", action="append",
                      help="Generate dependency for extra[s]")
    _parse_override_bdep(parser)
    options, args = parser.parse_args(argv)
    _handle_override_bdep(options)
    assert len(args) == 2, "One and only one command can be specified"
    command = args[1]
    assert os.path.exists(options.egg_info), "Does not exist: %s" % options.egg_info
    if command == 'depends':
        deps = _get_debian_dependencies(options.egg_info, extras=options.extras, exclude_extras=options.exclude_extras)
        print ', '.join(sorted(deps))
    elif command == 'provides':
        deps = _get_debian_provides(options.egg_info, extras=options.extras, exclude_extras=options.exclude_extras)
        print ', '.join(sorted(deps))
    else:
        raise Exception("Unknown command: %s" % command)
    return 0
_COMMANDS['depends'] = _COMMANDS['provides'] = _depends_or_provides

def _get_debian_provides(file, extras=None, exclude_extras=None):
    # get provides for extras
    pydeps = set([])
    base_dir = os.path.dirname(file)
    metadata = PathMetadata(base_dir, file)
    dist = Distribution.from_filename(file, metadata=metadata)
    if exclude_extras is not None:
        assert extras is None
        extras = set(dist.extras) - set(exclude_extras)
    if extras is None:
        extras = set(dist.extras)
    for i in extras:
        pydeps.add('%s-%s' % (py_to_bin(dist.project_name), i))
    return pydeps

def _get_debian_dependencies(file, extras=None, exclude_extras=None):
    """Returns a list of the format of the dpkg dependency info."""
    pydeps = set([])
    base_dir = os.path.dirname(file)
    metadata = PathMetadata(base_dir, file)
    dist = Distribution.from_filename(file, metadata=metadata)
    included_extras = set(dist.extras)
    if exclude_extras is not None:
        included_extras = included_extras - set(exclude_extras)
    if extras is not None:
        assert exclude_extras is None
        included_extras = extras
    for req in dist.requires(extras=included_extras):
        bin_pkg = py_to_bin(req.project_name)
        pkgs = []
        for extra in req.extras:
            pkgs.append('%s-%s' % (bin_pkg, extra))
        if req.specs:
            for spec in req.specs:
                op, version = spec
                op = _setuptools_debian_operators[op]
                if op is None:
                    continue
                dpkg_version = py_version_to_deb(version)
                pkgs.append('%s (%s %s)' % (bin_pkg, op, dpkg_version))
        elif not pkgs:
            pkgs = [bin_pkg]
        pydeps.update(pkgs)
    # Let's depend on the namespace packages as well.
    # This is needed to get __init__.py into the namespace packages.
    # See https://bugs.launchpad.net/van.pydeb/+bug/619294
    namespace_pkgs = dist._get_metadata('namespace_packages.txt')
    for pkg in namespace_pkgs:
        bin_pkg = py_to_bin(pkg)
        pydeps.add(bin_pkg)
    if extras is not None:
        # only give the dependencies of the metapackage
        pydeps = pydeps - _get_debian_dependencies(file, exclude_extras=dist.extras)
    return pydeps
