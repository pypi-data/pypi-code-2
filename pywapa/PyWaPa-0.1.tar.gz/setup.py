#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PyWaPa',
    version = '0.1',
    description = 'Python WhAtever Parser is a python markup converter from xml, json, yaml and ini to python dictionary. It allows also conversion between markup languages.',
    author = 'FELD Boris',
    author_email = 'lothiraldan@gmail.com',
    url = 'http://bitbucket.org/lothiraldan/pywapa',
    packages = ['pywapa', 'pywapa.parsers'],
    requires = ['pyyaml'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: XML',
    ],
)