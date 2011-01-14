# -*- coding: utf-8 -*-
'''
Roadmap
========

Roadmap is a routing library powered by regular expressions. Roadmap was
created to quickly map large amounts of input to functions. In the particular
case that sparked Roadmap's development, I was writing an IRC bot and I wanted
a fast (to code and to execute) way to map input strings to functions. Beyond an
IRC bot, I could also picture Roadmap being used to process data from a web API,
user input, a socket, or really any stream of data.

Links
======

* `website <https://github.com/lightcatcher/roadmap>`_
* `documentation <http://roadmap.readthedocs.org/>`_

'''

from setuptools import setup, find_packages

setup(
    name = 'roadmap',
    version = '0.1',
    url = 'https://github.com/lightcatcher/roadmap',
    author = 'Eric Martin',
    author_email = 'e.a.martin1337@gmail.com',
    description = 'Object routing framework powered by regular expressions',
    license = 'BSD',
    long_description = __doc__,
    py_modules = ['roadmap'],
    platforms = 'any',
    tests_require = ['attest'],
    test_loader = 'attest:Loader',
    test_suite = 'tests.roadmap_tests',
)