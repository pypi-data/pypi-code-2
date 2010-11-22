#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os

setup(name = "django-search",
      version='1.0',
      description='A django reusable app that adds a simple search to your project using a single tag',
      author='Ignacio Fernández Moreno',
      author_email='hellmoon666@gmail.com',
      url='http://bitbucket.org/hellmoon666/django-search',
      packages=['search','search.templatetags'],
      package_data={'search': ['templates/search/*.html']},
      long_description=open('README.txt').read(),
      zip_safe=True
)

