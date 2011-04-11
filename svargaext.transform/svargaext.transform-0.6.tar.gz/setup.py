#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'svargaext.transform',
    description = 'Source transformation module for Svarga framework',
    long_description = read('README'),
    license = 'BSD',
    version = '0.6',
    author = 'Alexander Solovyov',
    author_email = 'alexander@solovyov.net',
    url = 'http://hg.piranha.org.ua/svargaext.transform/',
    packages = ['svargaext.transform'],
    namespace_packages = ['svargaext'],
    install_requires = ['svarga', 'opster', 'clevercss'],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    platforms='any',
    )
