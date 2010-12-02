#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PyWaPa-3k',
    version = '0.1.1',
    description = 'Python WhAtever Parser is a python markup converter from xml, json, yaml and ini to python dictionary. It allows also conversion between markup languages. Python 3 compatible version.',
    author = 'FELD Boris',
    author_email = 'lothiraldan@gmail.com',
    url = 'http://bitbucket.org/lothiraldan/pywapa',
    packages = ['pywapa', 'pywapa.parsers'],
    requires = ['pyyaml'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: XML',
    ],
)