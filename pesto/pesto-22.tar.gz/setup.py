#!/usr/bin/env python
# Copyright (c) 2007-2011 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os
from setuptools import setup, find_packages

def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(
        os.path.join(
            os.path.dirname(__file__),
            *path
        ),
        'r'
    )
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()

setup(
    name='pesto',
    version=read('VERSION.txt').strip(),
    description='Library for WSGI applications',
    long_description=read('README.txt') + "\n\n" + read("CHANGELOG.txt"),
    author='Oliver Cope',
    license = 'BSD',
    author_email='oliver@redgecko.org',
    url='http://www.ollycope.com/software/pesto',
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[
        'repoze.lru>=0.3',
    ]
)
