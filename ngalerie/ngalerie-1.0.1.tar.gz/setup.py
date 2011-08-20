#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import sys

VERSION = "1.0.1" # find a better way to do so.

requires = ['PIL'] #pyexiv2
if sys.version_info < (2,7):
    requires.append('argparse')

setup(
    name = "ngalerie",
    version = VERSION,
    url = 'http://bitbucket.org/natim/ngallery/overview',
    author = u'Rémy HUBSCHER',
    author_email = 'remy.hubscher@ionyse.com',
    description = "A tool to manage Camera pictures (Rotate, Resize, Rename using EXIF).",
    long_description=open('README.rst').read(),
    packages = ['ngalerie'],
    include_package_data = True,
    install_requires = requires,
    scripts = ['bin/ngalerie'],
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Multimedia :: Graphics :: Editors',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)
