#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(
    name = 'django-ipgeo',
    description = 'API to ipgeobase.ru database',
    url = 'http://bitbucket.org/lorien/django-ipgeo/',
    version = '0.0.2',
    author = 'Grigoriy Petukhov',
    author_email = 'lorien@lorien.name',

    packages = find_packages(),
    include_package_data = True,

    license = "BSD",
    keywords = "",
    install_requires = [
        'django-common',
    ],
    classifiers= [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        #'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
