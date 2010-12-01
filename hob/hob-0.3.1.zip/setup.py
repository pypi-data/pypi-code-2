#!/usr/bin/env python

import sys
from hob import __version__, __author__, __author_email__, __program__, __doc__

try:
    from setuptools import setup, find_packages
    addl_args = dict(
        packages=find_packages(),
        entry_points={
        'console_scripts': [
            'hob = hob.script:run_exit',
            ],
        },
        test_suite='nose.collector',
        install_requires=['argparse>=1.0', 'mako'],
        )
except ImportError:
    print >> sys.stderr, "setup.py requires setuptools, install either pip or easy_install"
    sys.exit(1)

setup(
    name=__program__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url='http://bitbucket.org/scope/hob/',
    description=__doc__.splitlines()[0],
    long_description=open('README').read(),
    platforms=['any'],
    package_data = {'hob': [
            'templates/html-doc/*.mako',
            'templates/html-doc/*.css',
            'templates/js/*.mako',
            'templates/js/*.js',
            'templates/js/*.css',
            'templates/proto/*.mako',
            'templates/proto/*.proto',
            'templates/rst-doc/*.mako',
            'templates/proto/google/protobuf/*.proto',
            ]},
    license='New BSD License',
    keywords='scope protobuf',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Topic :: Software Development :: Code Generators',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development',
      ],
    **addl_args)
