#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import pidsim_models

setup(
    name = 'pidsim-models',
    version = pidsim_models.__version__,
    license = pidsim_models.__license__,
    description = pidsim_models.__description__,
    long_description = open('README.rst').read(),
    author = pidsim_models.__author__,
    author_email = pidsim_models.__email__,
    url = pidsim_models.__url__,
    platforms = 'any',
    packages = ['pidsim_models'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'pidsim>=1.0rc5',
    ],
)
