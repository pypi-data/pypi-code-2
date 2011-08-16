#!/usr/bin/env python

from setuptools import setup, find_packages
from version import get_git_version

setup(
    name='psycopg2-dateutils',
    version=get_git_version(),
    packages=find_packages(),
    install_requires=['psycopg2', 'dateutils'],
    author='Grzegorz Nosek',
    author_email='root@localdomain.pl',
    description='Use dateutils.relativedelta to represent PostgreSQL interval types',
    license='MIT',
    keywords='psycopg2 dateutils postgresql interval',
)
