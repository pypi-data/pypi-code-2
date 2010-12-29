#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <29-Dec-2010 12:52:20 PST by rich@noir.com>

import os

# try:
#     from setuptools import setup, find_packages
# except ImportError:
#     from ez_setup import use_setuptools
#     use_setuptools()
#     from setuptools import setup, find_packages

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='coding',
    version='0.001',
    author='K. Richard Pixley',
    author_email='rich@noir.com',
    description='An answer to the question of python enums.',
    license='MIT',
    keywords='enum coding',
    url='http://bitbucket.org/krp/coding',
    long_description=read(os.path.join('README')),
    setup_requires=[
    	'nose>=1.0.0',
#        'sphinx>=1.0.5',
    ],
    install_requires=[
    ],
    py_modules=['coding'],
    # test_suite='nose.collector',
    requires=[
    ],
    provides=[
        'coding',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
