#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-magnum',
    version='0.1',
    description='An on-demand PyPI cache. Can also serve non-PyPI packages from a local directory.',
    author='Nathan Reynolds',
    author_email='nath@nreynolds.me.uk',
    packages=find_packages(),
    package_data={'magnum': ['templates/magnum/*.html']},
    install_requires=[line.strip() for line in open('requirements.txt')],
)
