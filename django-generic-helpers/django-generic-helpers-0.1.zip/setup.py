#!/usr/bin/env python
from distutils.core import setup
import os

version='0.1'
package = 'generic_helpers'

setup(
    name = 'django-generic-helpers',
    version = version,
    author  = 'marazmiki',
    author_email = 'marazmiki@gmail.com',
    url = 'http://bitbucket.org/marazmiki/django-generic-helpers/',
    download_url = 'http://bitbucket.org/marazmiki/django-generic-helpers/get/tip.zip',

    description = 'This app makes it easy to display a map for a given address.',
    long_description = open('README.rst').read(),
    license = 'MIT license',
    requires = ['django (>=1.0)'],

    packages=['generic_helpers', 'generic_helpers.tests'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
