#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import os
import os.path
import sys

from setuptools import setup, Command
from distutils.command.build import build
from setuptools.command.bdist_egg import bdist_egg

topdir = os.path.split(os.path.abspath(__file__))[0]
if topdir == os.getcwd():
    topdir = ''


class gentab(Command):
    """Generate the PLY parse tables."""

    user_options = []
    description = 'generate parse tables'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        libdir = os.path.join(topdir, 'build', 'lib')
        sys.path.insert(0, libdir)
        from cli.parser import Parser
        parser = Parser()
        parser._write_tables()
        sys.stdout.write('generated parse tables in: %s\n' % libdir)


class mybuild(build):
    """Generate parse tables while building."""

    def run(self):
        build.run(self)
        self.run_command('gentab')


class mybdist_egg(bdist_egg):
    """Generate parse tables while building a binary egg."""

    def run(self):
        bdist_egg.run(self)
        self.run_command('gentab')


version_info = {
    'name': 'python-cli',
    'version': '1.2',
    'description': 'A toolkit for CLI construction',
    'author': 'Geert Jansen',
    'author_email': 'gjansen@redhat.com',
    'url': 'http://bitbucket.org/geertj/python-cli',
    'license': 'MIT',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 3' ],
}


setup(
    package_dir = { '': 'lib' },
    packages = [ 'cli', 'cli.command', 'cli.platform', 'cli.platform.posix' ],
    setup_requires = [ 'ply >= 3.3' ],
    install_requires = [ 'ply >= 3.3' ],
    entry_points = { 'console_scripts': [ 'cli-test = cli.main:main' ] },
    cmdclass = { 'build': mybuild, 'bdist_egg': mybdist_egg, 'gentab': gentab },
    use_2to3 = True,
    **version_info
)
