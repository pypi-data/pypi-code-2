#!/usr/bin/env python

from distutils.core import setup

setup(
    name='wordnik',
    platform="OSX",
    version="1.32",
    description='Simple wrapper around the wordnik API',
    author='Robin Walsh',
    author_email='robin@wordnik.com',
    url='http://developer.wordnik.com',
    packages = ['wordnik' ],
    package_data = {"wordnik": [ "endpoints/*.json" ]}
)
