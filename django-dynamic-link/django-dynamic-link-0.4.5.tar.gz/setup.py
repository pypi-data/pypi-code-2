#!/usr/bin/python
# -*- coding:utf-8 -*-
# This Python file uses the following encoding: utf-8

from setuptools import setup, find_packages
import sys
from dynamicLink import version

VERSION = version.VERSION_str

with open('README') as file:
    long_description = file.read()

REQUIRES = ['setuptools']
if sys.version_info < (2, 6):
    REQUIRES.append('python >= 2.6')
try:
    import django
    if django.VERSION < (1, 1):
        REQUIRES.extend(['django >= 1.1', 'django < 1.3'])
except ImportError:
    REQUIRES.extend(['django >= 1.1', 'django < 1.3'])

setup(name='django-dynamic-link',
      version=VERSION,
      description='A django file streaming application',
      long_description=long_description,
      author='A. Fritz',
      author_email='djangp-dynamic-link@bitzeit.eu',
      url='http://www.sources.e-blue.eu/de/pages/django/',
      download_url='https://bitbucket.org/catapela/django-dynamic-link/downloads',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      keywords="django file streaming dynamic links",
      classifiers=[
              'Development Status :: 4 - Beta',
              'Framework :: Django',
              'License :: OSI Approved :: BSD License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Environment :: Console',
              'Natural Language :: English',
              'Natural Language :: German',
              'Intended Audience :: Developers',
              'Intended Audience :: Information Technology',
              'Topic :: Internet',
              'Topic :: Utilities',
              ],
      install_requires = REQUIRES,
      zip_safe=False,
      )
