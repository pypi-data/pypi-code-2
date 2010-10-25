#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009 Andy Mikhailenko and contributors
#
#  This file is part of Django LJSync.
#
#  Django LJSync is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" django-ljsync setup "

from setuptools import *
import ljsync

setup(
    name         = 'django-ljsync',
    version      = ljsync.__version__,
    packages     = ['ljsync'],

    install_requires = ['python >= 2.4',
                        'django >= 1.0',
                        'django_autoslug >= 1.0.1'],

    description  = 'A LiveJournal to Django synchronizer',
    long_description = 'django-ljsync is an application made for two-way '\
                       'synchronization of your LiveJournal (LJ) blog to your '\
                       'Django-powered blog.',
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/django-ljsync/',
    download_url = 'http://bitbucket.org/neithere/django-ljsync/src/',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    keywords     = 'django livejournal blog sync',
    classifiers  = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Recovery Tools',
        'Topic :: Utilities',
    ],
)
