#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = 'dev-20110623-01'

setup(
    name = 'nust',
    version = version,
    packages  = find_packages('src'),
    package_dir  = {
        '':'src'
    },
    package_data = {
         '': ['*.conf','*.cfg'],
    },
    entry_points = {
        'console_scripts': ['nust=nust:main']
    },
    #install_requires = [],
    setup_requires = [
        'distribute>=0.6',
    ],

    author       = 'Sergey Vasilenko',
    author_email = 'sv@makeworld.ru',
    description  = 'This is a nginx\'s config parser and starter for uwsgi workers (tested on uwsgi 0.9.8)',
    license   = 'GPL',
    platforms = 'All',
    keywords  = 'nginx uwsgi starter',
    url  = 'http://dev.telemost.net/wiki/nginx_uwsgi_starter',

    classifiers = [
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Natural Language :: Russian',
        'Development Status :: 4 - Beta',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    zip_safe = False,
)


