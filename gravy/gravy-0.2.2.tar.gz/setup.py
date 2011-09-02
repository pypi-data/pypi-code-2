#!/usr/bin/env python

from distutils.core import setup

import sys
import os
srcdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, srcdir)
__version__ = '0.2.2'

readme = open("README").read()
changes = open("docs/changes.rst").read()
long_description = readme + "\n\n" + changes
requires = [
    'pip',
]

setup(
    name="gravy",
    version=__version__,
    author="Gerard Flanagan",
    author_email="grflanagan@gmail.com",
    description="Simple VCS wrapper",
    long_description=long_description,
    download_url="http://pypi.python.org/packages/source/g/gravy/gravy-%s.tar.gz" % __version__,
    py_modules=['gravy'],
    requires=requires,
)

