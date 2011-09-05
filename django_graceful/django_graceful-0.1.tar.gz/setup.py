#!/usr/bin/env python

from distutils.core import setup

setup(
        name='django_graceful',
        version='0.1',
        description='Django fastcgi deployment tool for easy management and graceful code updating',
        author='Andrey Bulgakov',
        author_email='mail@andreiko.ru',
        url='http://github.com/andreiko/django_graceful',
        packages=['django_graceful', 'django_graceful.management', 'django_graceful.management.commands'],
    )
