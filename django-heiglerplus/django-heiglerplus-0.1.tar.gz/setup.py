#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = 'django-heiglerplus',
    version = '0.1',
    packages = find_packages(),
    author = 'Heigler Rocha',
    author_email = 'lordheigler@gmail.com',
    description = 'A package with some usual apps to "usual" projects',
    include_package_data = True
)