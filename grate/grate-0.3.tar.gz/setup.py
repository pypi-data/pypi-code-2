#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name = 'grate',
    version = '0.3',
    packages = find_packages(),
    scripts = ['scripts/grated', 'scripts/grated-init'],
    author = 'Alex Lee',
    author_email = 'lee@ccs.neu.edu',
    url = '.',
    description = 'Single-purpose ssh server.',
    long_description = ('A single-purpose ssh server and Django app for '
        'serving git repositories.'),
    keywords = 'ssh django git',
    install_requires = [
        'Twisted>=10.1',
        'pymongo>=1.9',
        'mongoengine>=0.4',
        'pycrypto',
        'python-gflags>=1.3',
        'pyasn1>=0.0',
        'Django==1.2.5',
    ],
)
