#!/usr/bin/env python

import os
from setuptools import setup

import svargaext.sqlamigrate

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'svargaext.sqlamigrate',
    description = 'SQLAlchemy migrate module for Svarga framework',
    long_description = read('README'),
    license = 'BSD',
    version = svargaext.sqlamigrate.__version__,
    author = svargaext.sqlamigrate.__author__,
    author_email = svargaext.sqlamigrate.__email__,
    url = 'http://bitbucket.org/joes/svargaext.sqlamigrate/',
    namespace_packages = ['svargaext'],
    packages = ['svargaext.sqlamigrate'],
    include_package_data=True,
    install_requires = ['sqlalchemy-migrate'],
    classifiers = [
        'Development Status :: 4 - Beta',
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
