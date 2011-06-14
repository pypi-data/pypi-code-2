#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

##
## To deploy use 
## $ python ./setup.py sdist upload
##
## Your need increase version before it !!!
##

version = 'dev-20110615-01'

setup(
    name = 'asv_utils',
    version = version,
    packages  = find_packages('.'),
    install_requires = [
        'pytils>=0.2.3',
    ],
    setup_requires = [
        'distribute>=0.6',
    ],

    author       = 'Sergey Vasilenko',
    author_email = 'sv@makeworld.ru',
    description  = 'This is a set of common functions for other asv.* libs.',
    long_description = open('README.txt').read(),

    license   = 'GPL',
    platforms = 'All',
    keywords  = 'django asv tools',
    url  = 'http://bitbucket.org/xenolog/asv_utils/wiki/Home',

    classifiers = [
        'Environment :: Other Environment',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Natural Language :: Russian',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
)


