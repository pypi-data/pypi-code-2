#!/usr/bin/env python

from setuptools import setup

long_description = file('README.rst').read()

setup(
    name             = 'jsonproxy',
    version          = '0.1',
    description      = 'Gateway interface between non-standard types and JSON_ serialization.',
    long_description = long_description,
    author           = 'Wijnand Modderman-Lenstra',
    author_email     = 'maze@pyth0n.org',
    url              = 'https://maze.io/',
    packages         = ['jsonproxy'],
    license          = 'MIT',
    keywords         = 'JSON proxy',
 )
