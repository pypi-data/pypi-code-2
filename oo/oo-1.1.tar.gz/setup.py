#! /usr/bin/env python

# Public domain
# Byy Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk


import os


VERSION = '1.1'
NAME = 'oo'
MODULES = [NAME]
DESCRIPTION = 'You always wanted Python to moo? Now it can. Requires PyGame'

URL = "http://www.voidspace.org.uk/python/weblog/index.shtml"

LONG_DESCRIPTION = DESCRIPTION + """
::

    pip install oo
    python -moo

Requires PyGame 1.8 and Python 2.6 (or more recent).
"""

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
]

UNUSED = [
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

AUTHOR = 'Michael Foord'
AUTHOR_EMAIL = 'michael@voidspace.org.uk'
KEYWORDS = [] #("console interpreter expressions").split(' ')

params = dict(
    name=NAME,
    version=VERSION,
    py_modules=MODULES,

    # metadata for upload to PyPI
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=KEYWORDS,
    url=URL,
    classifiers=CLASSIFIERS,
)

from distutils.core import setup
setup(**params)
