#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name = 'grate',
    version = '0.2',
    packages = find_packages(),
    scripts = ['scripts/grated', 'scripts/grated-init'],
    author = 'Alex Lee',
    author_email = 'lee@ccs.neu.edu',
    url = '.',
    description = 'Single-purpose ssh server.',
    long_description = ('A single-purpose ssh server and Django app for '
        'serving git repositories.'),
    keywords = 'ssh django',
    install_requires = [
        'mongoengine >= 0.4',
        'Twisted >= 10.1',
        'python-gflags >= 1.3',
        'pyasn1 >= 0.0',
        'pycrypto',
        'Django==1.2.3',
    ],
)
