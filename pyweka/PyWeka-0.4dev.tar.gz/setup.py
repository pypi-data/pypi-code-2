#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Nicholas Tatonetti on 2009-12-16.
Copyright (c) 2009 Stanford University. All rights reserved.
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import find_packages, Extension
from numpy.distutils.core import setup

setup(name="PyWeka",
    version="0.4dev",
    description="PyWeka, a python WEKA wrapper.",
    long_description="""
    PyWeka
    A python WEKA Machine Learning wrapper.
    """,
    author="Nicholas P. Tatonetti & Guy Haskin Fernald",
    author_email="nick.tatonetti@stanford.edu & guyhf@stanford.edu",
    packages=find_packages(exclude='tests'),
    url="http://www-helix.stanford.edu",
    install_requires=['numpy>1.0.0','namedmatrix>0.1dev'])

