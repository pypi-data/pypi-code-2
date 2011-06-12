#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-table-prefix',
    description='experimental application for making table prefixes for'
        'tables that django creates',
    author='Egor V. Nazarkin, Vitaliy Kucheraviy',
    author_email='nimnull@gmail.com',
    version='0.0.5',
    py_modules=['table_prefix'],
    packages=find_packages(),
    license='BSD',
    long_description=open('README.txt').read(),
)
