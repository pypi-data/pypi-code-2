"""
Introduction
---------------

BlazeCommandHelper (BCH) is a framework that facilitates the quick creation of
shell and batch scripts.  It provides a core command (bch) which locates
sub-commands from system dirs, user dirs, and installed python packages
(through the "blazech.commands" endpoint).

Features
---------------

* locates plugin commands from various places
* provides logging facilities
* provides configuration file facilities (needs work)

The goal is to have an API that facilitates interaction between the environment,
command line options, and configuration files ala `pip <http://pip.openplans.org/configuration.html>`_.

Usage
---------------

Install BCH using easy_install or pip.  Once installed, create a file for your
first command:

    # *nix: ~/.blazech/command_hwp.py
    # %APPDATA%\.blazech\command_hwp.py
    from blazech.commands import BaseCommand

    class Command(BaseCommand):
        name = 'hello-world'
        help = 'say hello'

        def create_arguments(self):
            #self.parser is the argparse parser for this sub-command
            self.parser.add_argument(
                '-n', '--name',
                help='who do you want to say hello to',
                default='world'
            )

        def execute(self, args):
            print 'hello %s' % args.name

to run:

    # bch -h
    usage: bch [-h] [-v] [-q] {hello-world} ...

    positional arguments:
      {hello-world}
        hello-world     say hello
    <...snip...>

    $ bch hello-world
    hello world

    $ bch hello-world -n foo
    hello foo

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

Primary use cases work for me, but b/c of time constraints will probably move
forward slowly.

The `development version <http://bitbucket.org/rsyring/blazech/get/tip.zip#egg=BlazeCommandHelper-dev>`_
is installable with ``easy_install BlazeCommandHelper==dev``.
"""

import sys
force_setuptools = False
for command in ('upload', 'develop', 'egg_info',):
    if command in sys.argv:
        force_setuptools = True
if sys.platform == 'win32':
    force_setuptools = True
if force_setuptools:
    from setuptools import setup
else:
    from distutils.core import setup
import os


version = "0.1"

if sys.platform == 'win32':
    kw = dict(entry_points=dict(console_scripts=['bch=blazech:main']))
else:
    kw = dict(scripts=['scripts/bch'])

required_packages = ['BlazeUtils']
try:
    import argparse
except ImportError:
    required_packages.append('argparse')

setup(name='BlazeCommandHelper',
      version=version,
      description="A framework that facilitates shell and batch scripting in Python",
      long_description=__doc__,
      classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
      ],
      author='Randy Syring',
      author_email='rsyring@gmail.com',
      url='http://bitbucket.org/rsyring/blazech/',
      license='BSD',
      packages=['blazech'],
      install_requires=required_packages,
      zip_safe=False,
      entry_points="""
        [blazech.commands]
            hwp = blazech.tests.command_hwp:Command
      """,
      **kw)
