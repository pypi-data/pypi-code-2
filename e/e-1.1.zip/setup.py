#! /usr/bin/env python

# Public domain
# Idea from Georg Brandl. Foolishly done by Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk


import os


VERSION = '1.1'
NAME = 'e'
MODULES = [NAME]
DESCRIPTION = 'Evaluate and display command line expressions with ``python -me expr``'

URL = "http://www.voidspace.org.uk/python/weblog/index.shtml/"

LONG_DESCRIPTION = DESCRIPTION + """
For example::

    $ python -me 1+1
    2

Like `python -c` but no need for a print statement.

It allows multiple expressions::

    $ python -me 1+1 2+2
    2
    4

As a bonus, if the first argument is a module name then it will output the location
of the module source code::

    $ python -me os
    /Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/os.py

"""

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
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
KEYWORDS = ("console interpreter expressions").split(' ')

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
