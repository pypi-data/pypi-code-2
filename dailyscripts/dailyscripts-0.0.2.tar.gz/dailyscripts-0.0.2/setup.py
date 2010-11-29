#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = 'dailyscripts',
    version = '0.0.2',
    scripts = ['unpackall/unpackall'],

    zip_safe = True,


    #Metadata for PyPI
    url = 'http://github.com/spajus/dailyscripts/',
    author = 'Tomas Varaneckas',
    author_email = 'tomas.varaneckas@gmail.com',
    description = 'Daily Scripts. Utilities for every geek.',
    long_description = 'Daily Scripts. Utilities for every geek.',
    license = 'GPLv3',
    keywords = ['utils']
)
