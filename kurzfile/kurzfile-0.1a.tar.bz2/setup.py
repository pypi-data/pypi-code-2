#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A library to handle Kurzweil K-series synthesizer object files.

Currently this provides classes and functions to parse and represent .KRZ/.K25
and .K26 files and a script to list all objects contained in such files.

**This is still alpha-quality software!**

There is a public, read-only Subversion repository for this package located at
``svn://svn.chrisarndt.de/projects/kurzfile``. To check out a working copy of
the current trunk, do::

    svn co svn://svn.chrisarndt.de/projects/kurzfile/trunk kurzfile

"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

description = __doc__.splitlines()
long_description = "\n".join(description[2:])
description = description[0]

setup(
    name = 'kurzfile',
    version = '0.1a',
    description = description,
    keywords = 'kurzweil, music',
    author = 'Christopher Arndt',
    author_email = 'chris@chrisarndt.de',
    url = 'http://chrisarndt.de/projects/python-kurzfile/',
    download_url = 'http://chrisarndt.de/projects/python-kurzfile/download/',
    license = 'MIT License',
    long_description = long_description,
    platforms = 'POSIX, Windows, MacOS X',
    classifiers = [
        'Development Status :: 3 - Alpha',
        #'Environment :: MacOS X',
        #'Environment :: Win32 (MS Windows)',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Utilities'
    ],
    packages = ['kurzfile', 'kurzfile.scripts'],
    entry_points = {
        'console_scripts': [
            'k2list = kurzfile.scripts.k2list:main'
        ]
    }
)
