#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-tiendateca',
    version='0.0.2',
    description='Online Store Software for Django',
    author='Nando Quintana',
    author_email='nando@tiendateca.com',
    url='http://www.tiendateca.org/',
    packages=[
        'tiendateca',
    ],
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
)
