# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
import os
import shutil
import re
import pkg_resources
import subprocess
import tempfile
import sys
from cStringIO import StringIO
from ConfigParser import ConfigParser
import datetime

from collective.releaser import base
from collective.releaser.base import savewd

re_version = re.compile(r"""^version\s*=\s*(?:"|')(.*?)(?:"|')""",
                        re.MULTILINE|re.DOTALL)

re_name = re.compile(r"""name\s*=\s*(?:"|')(.*?)(?:"|')""",
                     re.MULTILINE|re.DOTALL)

def _get_setup():
    """returns setup content"""
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    return open(setup_py).read()

def get_version():
    """extract the version of the current package"""
    return get_metadata('version')

def get_name():
    """extract the name of the current package"""
    return get_metadata('name')

@savewd
def get_metadata(name, package_path=None):
    if package_path is not None:
        os.chdir(package_path)
    content = os.listdir(os.getcwd())
    if 'setup.py' not in content:
        raise ValueError('No setup.py file found in %s' % os.getcwd())
    name = name.replace('_', '-')
    command = '%s setup.py --%s' % (sys.executable, name)
    env = {'PYTHONPATH':os.pathsep.join(sys.path)}
    p = Popen(command, env=env, shell=True, stdout=PIPE, stderr=PIPE)
    return p.stdout.read().strip()

    import setuptools
    attrs = {}
    old = setuptools.setup
    try:
        def _setup(**kw):
            if name in kw:
                attrs[name] = kw[name]
        setuptools.setup = _setup
        import setup
    finally:
        setuptools.setup = old
    return attrs.get(name)

def raise_version(version):
    """raises the version"""

    # check version.txt
    for root, dirs, files in os.walk(os.getcwd()):
        for dirname in dirs:
            if not os.path.isdir(os.path.join(root, dirname, 'tests')):
                continue
            filename = os.path.join(root, dirname, 'version.txt')
            if not os.path.isfile(filename):
                continue
            f = open(filename, 'wb')
            try:
                f.write(version)
            finally:
                f.close()

    # check setup.py
    new_setup = re_version.sub("version = '%s'" % version, _get_setup())
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    f = open(setup_py, 'wb')
    try:
        f.write(new_setup)
    finally:
        f.close()

def check_tests():
    """runs the tests over the package"""
    try:
        base.check_call('%s setup.py test' % sys.executable, shell=True)
        return True
    except base.CalledProcessError:
        return False

def increment_changes():
    """increment changes"""

    author = get_metadata('maintainer')
    if author == 'UNKNOWN':
        author = get_metadata('author')
    if author == 'UNKNOWN':
        author = get_metadata('contact')
    if author != 'UNKNOWN':
        author = '[%s]' % author
    else:
        author = ''

    version = get_version()
    locations = (os.path.join(os.getcwd(), 'CHANGES'),
                 os.path.join(os.getcwd(), 'CHANGES.txt'))
    CHANGES = locations[0]
    if not os.path.exists(CHANGES) and os.path.exists(locations[1]):
        CHANGES = locations[1]

    year = datetime.datetime.now().strftime('%Y')
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    trunk_re = re.compile(r'^trunk \(.*\)$', re.DOTALL)
    trunk_line = 'trunk (%s)' % now
    bootstrap = [trunk_line, len(trunk_line) * '=', '',
                 '  - xxx ' + author, '']

    if os.path.exists(CHANGES):
        content = open(CHANGES).read()
        # let's replace the trunk with the current version and date
        version_line = '%s (%s)' % (version, now)
        underline = len(version_line) * '='
        content = content.split('\n')
        for index, line in enumerate(content):
            if trunk_re.match(line):
                content[index] = version_line
                content[index+1] = underline
                break
        content = bootstrap + content
    else:
        # no CHANGES file, let's create it
        content = bootstrap

    f = open(CHANGES, 'wb')
    try:
        f.write('\n'.join(content))
    finally:
        f.close()

def _get_svn_paths():
    """return paths"""
    version = get_version()
    url = base.get_svn_url()
    trunk = url
    if not url.endswith('/trunk'):
        raise base.ReleaseError('we are not in a trunk folder ! (%s)' % url)

    paths = {}
    paths['trunk'] = trunk
    paths['root'] = trunk.replace('/trunk', '/')
    paths['tag_root'] = '%stags' % paths['root']
    paths['branch_root'] = '%sbranches' % paths['root']
    paths['tag'] = '%stags/%s' % (paths['root'], version)
    paths['branch'] = '%sbranches/%s' % (paths['root'], version)
    return paths

def _checkout_tag():
    version = get_version()
    paths = _get_svn_paths()
    rep = tempfile.mkdtemp()
    base.svn_checkout(paths['tag'], rep)
    os.chdir(rep)

def _run_setup(*args):
    old_args = sys.argv
    sys.argv = [sys.argv[0]] + list(args)
    old_path = sys.path[:]
    sys.path.insert(0, os.getcwd())
    __import__('setup')
    del sys.modules['setup']
    sys.argv = old_args
    sys.path[:] = old_path

def pypi_upload(commands):
    """upload into pypi"""
    if base.has_svn_support():
        try:
            _checkout_tag()
        except base.ReleaseError:
            # inline releasing
            pass

    for command in commands:
        base.display('Running "%s"' % command)
        _run_setup(*command.split())

