# Copyright (c) 2010-2011, Found IT A/S and Piped Project Contributors.
# See LICENSE for details.
import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

setup(
    name = 'piped.contrib.validation',
    license = 'MIT',

    author = 'Found IT A/S',
    author_email = 'developers@piped.io',
    url = 'http://piped.io',

    packages = find_packages(where=here),
    namespace_packages = ['piped', 'piped.contrib'],

    version = '0.1.0',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Twisted',
        'Operating System :: OS Independent',
    ],
    description = 'FormEncode-like validation processor for Piped.',

    install_requires = ['piped', 'formencode', 'setuptools']
)