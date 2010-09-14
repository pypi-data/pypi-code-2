#!/usr/bin/env python
# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os.path
import pesto

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readfile(path):
    f = open(path, 'r')
    try:
        return f.read()
    finally:
        f.close()

setup(
    name='pesto',
    version=pesto.__version__,
    description='Library for WSGI applications',
    long_description=readfile('README.txt') + "\n\n" + readfile("CHANGELOG.txt"),
    author='Oliver Cope',
    license = 'BSD',
    author_email='oliver@redgecko.org',
    url='http://pesto.redgecko.org/',
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['pesto', 'pesto.session'],
    package_dir={'pesto': 'pesto'},
    scripts=[],
)
