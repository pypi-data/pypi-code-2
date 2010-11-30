#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'svargaext.clevercss',
    description = 'CleverCSS module for Svarga framework',
    long_description = read('README'),
    license = 'BSD',
    version = '0.3',
    author = 'Alexander Solovyov',
    author_email = 'alexander@solovyov.net',
    url = 'http://hg.piranha.org.ua/svargaext.clevercss/',
    packages = find_packages(),
    namespace_packages = ['svargaext'],
    install_requires = ['svarga', 'clevercss', 'opster'],
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
