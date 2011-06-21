#! /usr/bin/env python

from setuptools import setup

setup(
    name = "ooch",
    version = '1.0',
    description = 'python -mooch (sharing files on a LAN made kinda easy)',
    long_description = open('README.txt').read(),
    author = "Richard Jones",
    author_email = "richard@mechanicalcat.net",
    py_modules = ['ooch'],
    url = 'http://pypi.python.org/pypi/ooch',
    classifiers = [
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=['twisted'],
)

