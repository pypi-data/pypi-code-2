#!/usr/bin/env python

from os import path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

progname = 'sexpy'
from sexpy import __version__

README = '\n' + open(path.join(path.dirname(__name__), 'README')).read()
print(README)

setup(name='sexpy',
    version=__version__,
    description='S-expression syntax for Python',
    long_description=README,
    author='Ero-sennin',
    author_email='densetsu.no.ero.sennin@gmail.com',
    url='http://python.org/pypi/sexpy',
    license='GPL-2',
    platforms=['platform-independent'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['sexpy'],
    scripts=['sex.py'],
    )
