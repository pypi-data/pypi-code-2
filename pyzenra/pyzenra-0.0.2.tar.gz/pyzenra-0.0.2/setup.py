#!/usr/bin/env python

from setuptools import setup

version = '0.0.2'
name = 'pyzenra'
short_description = '`pyzenra` is zenrize your Japanese sentence.'
long_description = """\
`pyzenra` is zenrize your Japanese sentence.

Requirements
------------
* Python 2.5 or later (not support 3.x)

Features
--------
* zenrize Japanese sentence

Setup
-----
::

   $ easy_install pyzenra

History
-------
0.0.2 (2010-11-30)
~~~~~~~~~~~~~~~~~~
* add ZenraIgo class 

0.0.1 (2010-11-27)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Programming Language :: Python :: 2",
   "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    install_requires=[
        'igo-python'
    ],
    classifiers=classifiers,
    keywords=['text',],
    author="Masahito(Nakamura Masato) ",
    author_email="randomstep@gmail.com",
    url='https://bitbucket.org/ehren/pyzenra/',
    license="PSL",
    test_suite='tests.alltests.suite',
    )
