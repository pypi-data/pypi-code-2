#!/usr/bin/env python

from setuptools import setup, find_packages

import os
execfile(os.path.join('scuttle', 'version.py'))

setup(
    name = 'scuttle',
    version = VERSION,
    description = 'Scuttle is an analytics logging library',
    author = 'Samuel Stauffer',
    author_email = 'samuel@descolada.com',
    url = 'http://samuelks.com/scuttle/',
    packages = find_packages(),
    # test_suite = "tests",
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    # install_requires = [
    # ],
)
