#!/usr/bin/env python
import os
from setuptools import setup

PACKAGE = 'pypi-tools'
VERSION = '0.0.2'

setup(
    name = 'pypi-tools',
    version = VERSION,
    description = 'Command line PyPI search tool',
    author = 'Grigoriy Petukhov',
    author_email = 'lorien@lorien.name',
    url = 'http://bitbucket.org/lorien/pypi-tools',
    py_modules = ['pypi'],
    scripts = ['pypi'],
    license = "BSD",
    keywords = "django application development shortcuts helpers",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
