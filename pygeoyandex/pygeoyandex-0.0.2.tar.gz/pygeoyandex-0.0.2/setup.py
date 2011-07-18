#!/usr/bin/env python
#coding: utf-8
from setuptools import setup, find_packages

setup(
    name='pygeoyandex',
    version='0.0.2',
    author='Zakhar Zibarov',
    author_email='zakhar.zibarov@gmail.com',
    packages=find_packages(),
    url='http://bitbucket.org/zakhar/pygeoyandex',
    description = 'Yandex geocoding and reverse geocoding',

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
