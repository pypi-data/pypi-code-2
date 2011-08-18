#!/usr/bin/env python

from setuptools import setup

setup(
    name='crucible',
    version='0.1.0',
    description='Command line client to Crucible',
    author='Miki Tebeka',
    author_email='miki.tebeka@gmail.com',
    url='https://bitbucket.org/tebeka/crucible/src',
    license='MIT License',
    platforms=['any'],
    zip_safe=True,
    scripts=['scripts/crucible'],
)

